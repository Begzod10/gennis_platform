from datetime import datetime

from django.db.models import Exists, OuterRef

from .models import Lead, LeadCall, OperatorPercent


def calculate_leadcall_status_stats(selected_date=None, requests=None, branch_id=None, operator_lead=None):
    from django.db.models import Exists, OuterRef
    user = requests.user
    today = datetime.now().date()
    target_date = selected_date or today

    # If viewing past data, return cached
    if target_date < today:
        try:
            op = OperatorPercent.objects.get(user=user, date=target_date)
            return {
                "total_leads": op.total_lead,
                "progressing": op.progressing,
                "completed": op.accepted,
                "accepted_percentage": op.percent
            }, None
        except OperatorPercent.DoesNotExist:
            pass

    # Get today's leads assigned to the operator
    if operator_lead:
        today_leads = Lead.objects.filter(
            deleted=False,
            finished=False,
            branch_id=branch_id,
            operatorlead__in=operator_lead
        ).distinct()
    else:
        today_leads = Lead.objects.filter(
            deleted=False,
            finished=False,
            branch_id=branch_id
        ).distinct()

    # Leads that had a call today
    leadcall_today_ids = LeadCall.objects.filter(
        lead__in=today_leads,
        created=target_date,
        deleted=False
    ).values_list('lead_id', flat=True)

    # Split by completed vs progressing
    completed = today_leads.filter(id__in=leadcall_today_ids).count()
    progressing = today_leads.exclude(id__in=leadcall_today_ids).count()
    total_leads = today_leads.count()
    print(f"Completed: {completed}, Progressing: {progressing}, Total: {total_leads}")
    # status=True count (regardless of date)
    status_true_count = LeadCall.objects.filter(
        lead__in=today_leads,
        status=True,
        deleted=False
    ).values('lead_id').distinct().count()

    # Percentage
    if total_leads == 0:
        accepted_percentage = 0
    else:
        accepted_percentage = round((completed / total_leads) * 100, 2)

    # Save to DB if today
    if target_date == today and user.groups.filter(name='operator').exists():
        print('exists')
        OperatorPercent.objects.update_or_create(
            user=user,
            date=target_date,
            defaults={
                "percent": accepted_percentage,
                "progressing": progressing,
                "total_lead": total_leads,
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
    }, leadcall_today_ids


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
    print("operators_percent", len(operators_percent))
    accepted = 0
    progressing = 0
    percentage = 0
    total_leads = 0
    for operator in operators_percent:
        print("accepted", operator.accepted, "total_lead", operator.total_lead, "percent", operator.percent,
              "progressing", operator.progressing)
        accepted += operator.accepted
        progressing += operator.progressing
        percentage += operator.percent
        total_leads += operator.total_lead

    return {
        "status_true_count": 0,
        "total_leads": total_leads,
        "progressing": progressing,
        "completed": accepted,
        "accepted_percentage": round(percentage / operators_percent.count(), 2) if operators_percent.count() else 0
    }
