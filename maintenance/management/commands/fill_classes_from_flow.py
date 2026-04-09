from django.core.management.base import BaseCommand
from school_time_table.models import ClassTimeTable


class Command(BaseCommand):
    help = "Fill classes field from flow for old ClassTimeTable records"

    def handle(self, *args, **options):
        qs = ClassTimeTable.objects.filter(
            flow__isnull=False,
            classes__isnull=True
        ).select_related('flow')

        updated = 0

        for ct in qs:
            if ct.flow and ct.flow.classes:
                ct.classes = ct.flow.classes
                ct.save(update_fields=['classes'])
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Updated {updated} ClassTimeTable records"
        ))
