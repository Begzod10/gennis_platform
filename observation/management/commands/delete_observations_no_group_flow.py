from django.core.management.base import BaseCommand
from django.db.models import Q

from teachers.models import Teacher
from observation.models import TeacherObservationDay, TeacherObservationSchedule


class Command(BaseCommand):
    help = "Delete observation data for teachers who have no groups and no flows"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview what will be deleted without actually deleting",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Teachers who have NO active groups and NO flows
        teachers_with_activity = Teacher.objects.filter(
            Q(group__deleted=False) | Q(flow__isnull=False)
        ).values_list("id", flat=True).distinct()

        inactive_teacher_ids = (
            Teacher.objects
            .filter(deleted=False)
            .exclude(id__in=teachers_with_activity)
            .values_list("id", flat=True)
        )

        obs_days = TeacherObservationDay.objects.filter(teacher_id__in=inactive_teacher_ids)
        schedules = TeacherObservationSchedule.objects.filter(
            Q(observer_id__in=inactive_teacher_ids) |
            Q(observed_teacher_id__in=inactive_teacher_ids)
        )

        obs_count = obs_days.count()
        sched_count = schedules.count()
        teacher_count = len(inactive_teacher_ids)

        self.stdout.write(
            f"Teachers without groups or flows: {teacher_count}\n"
            f"TeacherObservationDay records to delete: {obs_count} "
            f"(+ cascades TeacherObservation rows)\n"
            f"TeacherObservationSchedule records to delete: {sched_count}"
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — nothing deleted."))
            return

        deleted_sched, _ = schedules.delete()
        deleted_days, _ = obs_days.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {deleted_sched} schedule records and "
                f"{deleted_days} observation day records (+ cascaded rows)."
            )
        )
