from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import StudentDailyAttendance, StudentMonthlySummary, GroupMonthlySummary
import calendar


def rebuild_group_summary(monthly_summary):
    group = monthly_summary.group
    year = monthly_summary.year
    month = monthly_summary.month

    summary, _ = GroupMonthlySummary.objects.get_or_create(
        group=group, year=year, month=month
    )

    days_in_month = calendar.monthrange(year, month)[1]
    all_days = [
        i for i in range(1, days_in_month + 1)
        if calendar.weekday(year, month, i) != 6
    ]

    students_data = []
    students = group.students.all()

    for student in students:
        # default: None (id va status bo‘sh)
        day_map = {str(d): {"id": None, "status": None} for d in all_days}

        daily_records = StudentDailyAttendance.objects.filter(
            monthly_summary__student=student,
            monthly_summary__group=group,
            monthly_summary__year=year,
            monthly_summary__month=month
        )

        for rec in daily_records:
            day_map[str(rec.day.day)] = {
                "id": rec.id,
                "status": rec.status,
                "reason": rec.reason
            }

        students_data.append({
            "student": {
                "id": student.id,
                "name": student.user.name,
                "surname": student.user.surname,
            },
            "days": day_map
        })

    summary.stats = students_data
    summary.save(update_fields=["stats"])


@receiver(post_save, sender=StudentDailyAttendance)
def update_group_summary_on_save(sender, instance, **kwargs):
    rebuild_group_summary(instance.monthly_summary)


@receiver(post_delete, sender=StudentDailyAttendance)
def update_group_summary_on_delete(sender, instance, **kwargs):
    rebuild_group_summary(instance.monthly_summary)
