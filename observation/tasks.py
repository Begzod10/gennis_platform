import logging
from celery import shared_task, group
from datetime import date, timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def generate_observation_schedule_task(self, branch_id: int, start_date_str: str) -> dict:
    """
    Build a full teacher-observation cycle for the given branch.

    Args:
        branch_id:      Branch pk
        start_date_str: ISO date string (YYYY-MM-DD) — week 1 starts here

    Returns a summary dict that Celery stores as the task result.
    """
    from branch.models import Branch
    from observation.models import TeacherObservationCycle, TeacherObservationSchedule
    from school_time_table.models import ClassTimeTable
    from teachers.models import Teacher

    logger.info("generate_observation_schedule_task started: branch=%s start=%s", branch_id, start_date_str)

    try:
        start_date = date.fromisoformat(start_date_str)
    except ValueError as exc:
        logger.error("Invalid start_date: %s", start_date_str)
        raise ValueError(f"start_date must be YYYY-MM-DD, got: {start_date_str}") from exc

    try:
        branch = Branch.objects.get(id=branch_id)
    except Branch.DoesNotExist:
        logger.error("Branch %s not found", branch_id)
        raise

    teachers = list(
        Teacher.objects.filter(branches=branch, deleted=False)
        .select_related("user")
        .order_by("id")
    )

    if len(teachers) < 2:
        msg = f"Branch {branch_id} has fewer than 2 active teachers — schedule not generated."
        logger.warning(msg)
        return {"success": False, "detail": msg}

    # teacher_id -> first ClassTimeTable in this branch
    timetable_map = {}
    for ct in ClassTimeTable.objects.filter(branch=branch, teacher__in=teachers):
        if ct.teacher_id not in timetable_map:
            timetable_map[ct.teacher_id] = ct

    cycle = TeacherObservationCycle.objects.create(branch=branch, start_date=start_date)

    schedules_to_create = []
    for obs_idx, observer in enumerate(teachers):
        others = [t for t in teachers if t.id != observer.id]
        # Rotate start position so each observer gets a different week-1 pair
        offset = (obs_idx * 2) % len(others)
        others = others[offset:] + others[:offset]
        week = 1
        for i in range(0, len(others), 2):
            pair = others[i: i + 2]
            for observed in pair:
                schedules_to_create.append(
                    TeacherObservationSchedule(
                        cycle=cycle,
                        observer=observer,
                        observed_teacher=observed,
                        week=week,
                        time_table=timetable_map.get(observed.id),
                    )
                )
            week += 1

    TeacherObservationSchedule.objects.bulk_create(schedules_to_create)

    total_weeks = max((s.week for s in schedules_to_create), default=0)

    result = {
        "success": True,
        "cycle_id": cycle.id,
        "branch_id": branch_id,
        "start_date": start_date_str,
        "teachers_count": len(teachers),
        "total_weeks": total_weeks,
        "schedules_created": len(schedules_to_create),
    }
    logger.info("generate_observation_schedule_task done: %s", result)
    return result


@shared_task
def generate_observation_schedules_for_branches(branch_ids: list, next_monday_str: str) -> dict:
    """
    Spawns one generate_observation_schedule_task per branch in parallel.
    Called automatically after update_school_time_table_task finishes.

    Args:
        branch_ids:       List of branch PKs that had timetable rows created.
        next_monday_str:  ISO date of next week's Monday (YYYY-MM-DD) — used as cycle start_date.
    """
    if not branch_ids:
        logger.info("generate_observation_schedules_for_branches: no branches, skipping.")
        return {"skipped": True}

    logger.info(
        "Spawning observation schedule tasks for %d branch(es), start=%s",
        len(branch_ids),
        next_monday_str,
    )

    job = group(
        generate_observation_schedule_task.s(
            branch_id=bid, start_date_str=next_monday_str
        )
        for bid in branch_ids
    )
    result = job.apply_async()

    return {
        "branches": branch_ids,
        "next_monday": next_monday_str,
        "group_id": result.id,
    }


@shared_task
def test_generate_observation_schedule_task(branch_id: int) -> dict:
    """
    TEST TASK — run manually to verify schedule generation for the current week.

    Uses this week's Monday as start_date so the generated cycle is immediately
    on week 1 and /schedule/current_week/ returns data right away.

    Usage from Django shell:
        from observation.tasks import test_generate_observation_schedule_task
        test_generate_observation_schedule_task.delay(branch_id=1)
    """
    today = date.today()
    current_monday = today - timedelta(days=today.weekday())
    start_date_str = current_monday.isoformat()

    logger.info(
        "test_generate_observation_schedule_task: branch=%s, start_date=%s",
        branch_id,
        start_date_str,
    )

    return generate_observation_schedule_task(
        branch_id=branch_id,
        start_date_str=start_date_str,
    )
