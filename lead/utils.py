from datetime import datetime

from django.db.models import Exists, OuterRef

from .models import Lead, LeadCall, OperatorPercent


def calculate_leadcall_status_stats(selected_date=None, requests=None, branch_id=None, operator_lead=None):
    from django.db.models import Exists, OuterRef, Q
    user = requests.user
    today = datetime.now().date()
    target_date = selected_date or today

    # If viewing historical stats (cached in DB)
    if target_date < today:
        try:
            op = OperatorPercent.objects.get(user=user, date=target_date)
            return {
                "total_leads": op.accepted + op.total_lead,
                "progressing": op.total_lead,
                "completed": op.accepted,
                "accepted_percentage": op.percent
            }
        except OperatorPercent.DoesNotExist:
            pass

    # Get relevant leads
    if operator_lead:
        leads = Lead.objects.filter(
            deleted=False,
            branch_id=branch_id,
            operatorlead__in=operator_lead
        )
    else:
        leads = Lead.objects.filter(
            deleted=False,
            branch_id=branch_id
        )

    # ✅ Leads with LeadCall created today
    leads_with_today_created_call = leads.annotate(
        has_today_leadcall=Exists(
            LeadCall.objects.filter(
                lead=OuterRef('pk'),
                created=target_date,
                deleted=False
            )
        )
    ).filter(has_today_leadcall=True)

    completed = leads_with_today_created_call.count()

    # 🔄 Leads with no LeadCall at all (excluding delay or created today)
    leads_with_no_leadcall = leads.annotate(
        has_any_call=Exists(
            LeadCall.objects.filter(
                lead=OuterRef('pk'),
                deleted=False
            ).exclude(
                Q(created=target_date) | Q(delay=target_date)
            )
        )
    ).filter(has_any_call=False).exclude(id__in=leads_with_today_created_call)

    progressing = leads_with_no_leadcall.count()

    total_leads = progressing + completed
    # print("total_leads", total_leads)
    print("completed", completed)
    print("progressing", progressing)
    # ✅ Leads that had status=True at least once
    status_true_count = LeadCall.objects.filter(
        lead__in=leads,
        status=True,
        deleted=False
    ).values('lead').distinct().count()

    # % Calculation
    if completed == 0 and progressing == 0:
        accepted_percentage = 0
    elif progressing == 0 and completed > 0:
        accepted_percentage = 100
    else:
        accepted_percentage = round((completed / total_leads) * 100, 2) if total_leads else 0

    # Save today's result into DB
    if target_date == today and user.groups.filter(name='operator').exists():
        OperatorPercent.objects.update_or_create(
            user=user,
            date=target_date,
            defaults={
                "percent": accepted_percentage,
                "total_lead": progressing,
                "accepted": completed,
                "branch_id": branch_id
            }
        )

    return {
        "status_true_count": status_true_count,
        "total_leads": total_leads,
        "progressing": progressing,
        "completed": completed,
        "accepted_percentage": accepted_percentage
    }


def calculate_all_percentage(selected_date=None, branch_id=None):
    from user.models import CustomUser
    operators = CustomUser.objects.filter(
        branch_id=branch_id,
        customautogroup__group__name='operator',
        customautogroup__deleted=False
    )
    if selected_date is None:
        selected_date = datetime.now().date()
    operators_percent = OperatorPercent.objects.filter(user__in=operators, date=selected_date, branch_id=branch_id)
    accepted = 0
    progressing = 0
    percentage = 0
    for operator in operators_percent:
        accepted += operator.accepted
        progressing += operator.total_lead
        percentage += operator.percent

    return {
        "status_true_count": 0,
        "total_leads": accepted + progressing,
        "progressing": progressing,
        "completed": accepted,
        "accepted_percentage": round(percentage / operators_percent.count(), 2) if operators_percent.count() else 0
    }
