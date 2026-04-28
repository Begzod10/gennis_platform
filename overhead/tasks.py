import logging
from datetime import date

from celery import shared_task
from django.utils import timezone

from branch.models import Branch
from overhead.models import OverheadType, OverheadTypeLog

logger = logging.getLogger(__name__)


@shared_task(name='overhead.generate_monthly_overhead_logs')
def generate_monthly_overhead_logs():
    """
    Runs on the 1st of every month.
    Creates OverheadTypeLog entries for all fixed (non-changeable) overhead types
    for the new month so admins have a ready reminder list — one per branch.
    """
    try:
        today = timezone.localtime().date()
        month_date = today.replace(day=1)

        fixed_types = OverheadType.objects.filter(
            changeable=False,
            cost__isnull=False,
            deleted=False,
        )
        branches = Branch.objects.all()

        created = 0
        for ot in fixed_types:
            for branch in branches:
                exists = OverheadTypeLog.objects.filter(
                    overhead_type=ot,
                    branch_id=branch.id,
                    date=month_date,
                ).exists()
                if not exists:
                    OverheadTypeLog.objects.create(
                        overhead_type=ot,
                        cost=ot.cost,
                        is_paid=False,
                        is_prepaid=False,
                        branch_id=branch.id,
                        date=month_date,
                    )
                    created += 1

        logger.info(f"generate_monthly_overhead_logs: created {created} logs for {month_date}")
        return {'success': True, 'created': created, 'month': str(month_date)}

    except Exception as exc:
        logger.error(f"generate_monthly_overhead_logs failed: {exc}")
        return {'success': False, 'error': str(exc)}
