from django.core.management.base import BaseCommand
from django.db import transaction

from branch.models import Branch
from school_time_table.models import Hours, ClassTimeTable


class Command(BaseCommand):
    help = "Clone global Hours to all branches and remap ClassTimeTable hours"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting migration..."))

        base_hours = Hours.objects.filter(branch__isnull=True)
        branches = Branch.objects.all().exclude(location__isnull=True)

        created_count = 0

        for hour in base_hours:
            for branch in branches:
                exists = Hours.objects.filter(
                    branch=branch,
                    old_id=hour.id
                ).exists()

                if not exists:
                    Hours.objects.create(
                        start_time=hour.start_time,
                        end_time=hour.end_time,
                        name=hour.name,
                        order=hour.order,
                        branch=branch,
                        old_id=hour.id
                    )
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Hours cloned: {created_count}"))

        updated_count = 0

        timetables = ClassTimeTable.objects.select_related("hours", "branch")

        for timetable in timetables:
            old_hour = timetable.hours

            if old_hour and old_hour.branch is None:
                new_hour = Hours.objects.filter(
                    branch=timetable.branch,
                    old_id=old_hour.id
                ).first()

                if new_hour:
                    timetable.hours = new_hour
                    timetable.save(update_fields=["hours"])
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"ClassTimeTable updated: {updated_count}"))

        self.stdout.write(self.style.SUCCESS("Migration completed successfully ✅"))
