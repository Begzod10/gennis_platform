"""
Delete LessonPlanFile rows whose status is 'failed'.

Usage:
    python manage.py delete_failed_lesson_plans --dry-run
    python manage.py delete_failed_lesson_plans
    python manage.py delete_failed_lesson_plans --keep-files
    python manage.py delete_failed_lesson_plans --teacher-id 139 --term-id 4
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from lesson_plan.models import LessonPlanFile


class Command(BaseCommand):
    help = "Delete lesson plan files with status='failed' (and remove their uploaded files from storage)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without touching anything.",
        )
        parser.add_argument(
            "--keep-files",
            action="store_true",
            help="Delete DB rows only; leave uploaded files on disk / storage.",
        )
        parser.add_argument(
            "--teacher-id",
            type=int,
            default=None,
            help="Limit deletion to a single teacher.",
        )
        parser.add_argument(
            "--term-id",
            type=int,
            default=None,
            help="Limit deletion to a single term.",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        keep_files: bool = options["keep_files"]
        teacher_id = options["teacher_id"]
        term_id = options["term_id"]

        qs = LessonPlanFile.objects.filter(status=LessonPlanFile.Status.FAILED)
        if teacher_id is not None:
            qs = qs.filter(teacher_id=teacher_id)
        if term_id is not None:
            qs = qs.filter(term_id=term_id)

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("No failed lesson plans to delete."))
            return

        self.stdout.write(f"Found {total} failed lesson plan file(s).")
        for lpf in qs.only("id", "teacher_id", "term_id", "subject_id", "file", "feedback")[:50]:
            self.stdout.write(
                f"  - id={lpf.id} teacher={lpf.teacher_id} term={lpf.term_id} "
                f"subject={lpf.subject_id} file={lpf.file.name!r} "
                f"feedback={(lpf.feedback or '')[:60]!r}"
            )
        if total > 50:
            self.stdout.write(f"  ... and {total - 50} more")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — nothing deleted."))
            return

        deleted_files = 0
        deleted_rows = 0
        with transaction.atomic():
            for lpf in qs.iterator():
                if not keep_files and lpf.file:
                    try:
                        lpf.file.delete(save=False)
                        deleted_files += 1
                    except Exception as exc:
                        self.stderr.write(
                            self.style.WARNING(
                                f"  failed to delete file for id={lpf.id}: {exc}"
                            )
                        )
                lpf.delete()
                deleted_rows += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {deleted_rows} row(s)"
                + ("" if keep_files else f" and {deleted_files} stored file(s)")
                + "."
            )
        )
