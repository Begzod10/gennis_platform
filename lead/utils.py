from django.db.models import Exists, OuterRef
from django.utils import timezone

from .models import Lead, LeadCall, OperatorPercent


# def calculate_leadcall_status_stats(selected_date=None, requests=None, branch_id=None):
def calculate_leadcall_status_stats(selected_date=None, requests=None):
    user = requests.user
    today = timezone.now().date()
    target_date = selected_date or today

    if target_date < today:
        try:
            op = OperatorPercent.objects.get(user=user, date=target_date)
            return {
                "status_true_count": op.accepted,
                "total_leads": op.total_lead,
                "accepted_percentage": op.percent
            }
        except OperatorPercent.DoesNotExist:
            pass

    # Barcha aktiv leadlar
    # leads = Lead.objects.filter(deleted=False, branch_id=branch_id)
    leads = Lead.objects.filter(deleted=False)

    # Completed: bugungi sana bilan yaratilgan LeadCall mavjud bo‘lsa
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

    # Progressing: 2ta holat
    # 1) Umuman LeadCall yo‘q
    # 2) LeadCall bor, lekin delay == today, va created != today
    leads_with_no_leadcall = leads.annotate(
        has_any_call=Exists(
            LeadCall.objects.filter(
                lead=OuterRef('pk'),
                deleted=False
            )
        )
    ).filter(has_any_call=False)

    leads_with_delay_today_but_not_created_today = leads.annotate(
        has_delay_today_but_no_created_today=Exists(
            LeadCall.objects.filter(
                lead=OuterRef('pk'),
                delay=target_date,
                deleted=False
            ).exclude(created=target_date)
        )
    ).filter(has_delay_today_but_no_created_today=True)

    progressing = leads_with_no_leadcall.count() + leads_with_delay_today_but_not_created_today.count()

    total_leads = completed + progressing

    status_true_count = LeadCall.objects.filter(
        lead__in=leads,
        status=True,
        deleted=False
    ).values('lead').distinct().count()
    if completed == 0 and progressing == 0:
        accepted_percentage = 0
    elif progressing == 0 and completed > 0:
        accepted_percentage = 100
    else:
        accepted_percentage = round((completed / (progressing + completed)) * 100, 2) if total_leads else 0

    # Saqlash bugungi kunga
    if target_date == today:
        OperatorPercent.objects.update_or_create(
            user=user,
            date=target_date,
            defaults={
                "percent": accepted_percentage,
                "total_lead": total_leads,
                "accepted": status_true_count
            }
        )

    return {
        "status_true_count": status_true_count,
        "total_leads": total_leads,
        "progressing": progressing,
        "completed": completed,
        "accepted_percentage": accepted_percentage
    }
