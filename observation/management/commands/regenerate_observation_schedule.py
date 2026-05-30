"""
Regenerate the latest TeacherObservationCycle for one branch or every school branch.

Drops the existing cycle (cascades to its TeacherObservationSchedule rows), then
re-runs `generate_observation_schedule_task` which now uses the balanced
cyclic-offset round-robin (see `observation/tasks.py:_build_cyclic_schedule`).

Usage:
    python manage.py regenerate_observation_schedule --dry-run
    python manage.py regenerate_observation_schedule --branch-id 5
    python manage.py regenerate_observation_schedule --branch-id 5 --start-date 2026-06-01
    python manage.py regenerate_observation_schedule --sync
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from branch.models import Branch
from observation.models import TeacherObservationCycle
from observation.tasks import generate_observation_schedule_task


class Command(BaseCommand):
    help = (
        "Regenerate the most recent observation cycle for a branch (or every school "
        "branch) using the balanced cyclic-offset round-robin."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--branch-id",
            type=int,
            default=None,
            help="Only regenerate this branch. If omitted, every school branch is regenerated.",
        )
        parser.add_argument(
            "--start-date",
            type=str,
            default=None,
            help="ISO date (YYYY-MM-DD) to use as cycle start_date. Defaults to the "
                 "existing cycle's start_date, or next Monday if the branch has no cycle.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be regenerated without changing anything.",
        )
        parser.add_argument(
            "--sync",
            action="store_true",
            help="Run the generation inline instead of dispatching via Celery .delay().",
        )

    def handle(self, *args, **options):
        branch_id: int | None = options["branch_id"]
        start_date_arg: str | None = options["start_date"]
        dry_run: bool = options["dry_run"]
        sync: bool = options["sync"]

        if start_date_arg:
            try:
                date.fromisoformat(start_date_arg)
            except ValueError as exc:
                raise CommandError(f"--start-date must be YYYY-MM-DD, got: {start_date_arg}") from exc

        if branch_id is not None:
            branches = Branch.objects.filter(id=branch_id)
            if not branches.exists():
                raise CommandError(f"Branch id={branch_id} not found.")
        else:
            branches = Branch.objects.filter(location__system__name="school")

        branch_count = branches.count()
        if branch_count == 0:
            self.stdout.write(self.style.WARNING("No matching branches."))
            return

        next_monday = (date.today() + timedelta(days=(7 - date.today().weekday()) % 7 or 7)).isoformat()

        planned = []
        for branch in branches:
            cycle = (
                TeacherObservationCycle.objects.filter(branch=branch)
                .order_by("-created_at")
                .first()
            )
            if start_date_arg:
                start_date_str = start_date_arg
            elif cycle:
                start_date_str = cycle.start_date.isoformat()
            else:
                start_date_str = next_monday
            planned.append((branch, cycle, start_date_str))

        self.stdout.write(f"Branches to regenerate: {branch_count}")
        for branch, cycle, start_date_str in planned:
            cycle_desc = (
                f"cycle id={cycle.id} start={cycle.start_date.isoformat()}"
                if cycle
                else "no existing cycle"
            )
            self.stdout.write(
                f"  - branch id={branch.id} name={branch.name!r} | {cycle_desc} | "
                f"new start_date={start_date_str}"
            )

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — nothing changed."))
            return

        deleted_cycles = 0
        regenerated = 0
        with transaction.atomic():
            for branch, cycle, _ in planned:
                if cycle:
                    cycle.delete()  # cascades schedules
                    deleted_cycles += 1

        for branch, _cycle, start_date_str in planned:
            if sync:
                generate_observation_schedule_task(branch_id=branch.id, start_date_str=start_date_str)
            else:
                generate_observation_schedule_task.delay(
                    branch_id=branch.id, start_date_str=start_date_str
                )
            regenerated += 1

        mode = "synchronously" if sync else "queued via Celery"
        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {deleted_cycles} existing cycle(s); "
                f"regenerated {regenerated} branch(es) {mode}."
            )
        )
