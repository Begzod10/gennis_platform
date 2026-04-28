import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gennis_platform.settings")
django.setup()

from branch.models import Branch
from observation.models import TeacherObservationCycle
from observation.tasks import generate_observation_schedule_task

# Delete all existing cycles (cascades to schedules)
deleted, _ = TeacherObservationCycle.objects.all().delete()
print(f"Deleted {deleted} records (cycles + schedules)")

branches = Branch.objects.filter(location__system__name="school")
print(f"Found {branches.count()} school branches\n")

for branch in branches:
    generate_observation_schedule_task.delay(branch_id=branch.id, start_date_str="2026-04-27")
    print(f"Queued branch {branch.id} - {branch.name}")
