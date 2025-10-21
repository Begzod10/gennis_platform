from datetime import datetime, timedelta
from django.db import transaction
from celery import shared_task
from .models import ClassTimeTable
from students.models import Student, StudentSubject, StudentSubjectCount
from group.models import Group, GroupSubjects, GroupSubjectsCount
from django.utils import timezone


@shared_task
def update_school_time_table_task():
    """
    1) Find all lessons in the current week (Mon→Sun).
    2) For each lesson, create copies for the next 6 days (date+1 ... date+6).
    3) For each created lesson, create/update:
       - GroupSubjectsCount (bucketed by month_date)
       - StudentSubjectCount (bucketed by month_date)
       and backfill monthly aggregates on GroupSubjects.count / StudentSubject.count.
    """
    # If your project uses USE_TZ=True, localdate is safe.
    today = timezone.localdate()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    monday = "2025-09-29"
    sunday = "2025-10-04"
    monday = datetime.strptime(monday, "%Y-%m-%d").date()
    sunday = datetime.strptime(sunday, "%Y-%m-%d").date()
    print("========== SCHOOL TIMETABLE UPDATE (Next 6 Days) ==========")
    print("Today:", today.strftime("%A"), today)
    print("This week's Monday:", monday.strftime("%A"), monday)
    print("This week's Sunday:", sunday.strftime("%A"), sunday)

    source_lessons = (
        ClassTimeTable.objects
        .filter(date__gte=monday, date__lte=sunday)
        .select_related('subject', 'teacher', 'hours', 'room', 'group', 'flow')
        .prefetch_related('students')
    )

    total_src = source_lessons.count()
    print(f"Found {total_src} lessons in the current week.")
    if total_src == 0:
        print("❌ Manba haftada dars topilmadi (No lessons found).")
        return "No lessons found"

    created_count = 0
    skipped_count = 0

    with transaction.atomic():
        for old in source_lessons:
            # SAME WEEKDAY NEXT WEEK
            new_date = old.date + timedelta(days=7)
            month_date = datetime(new_date.year, new_date.month, 1)

            exists = ClassTimeTable.objects.filter(
                date=new_date,
                subject=old.subject,
                teacher=old.teacher,
                hours_id=old.hours_id,
                room_id=old.room_id,
                group_id=getattr(old, "group_id", None),
                flow_id=getattr(old, "flow_id", None),
            ).exists()
            if exists:
                skipped_count += 1
                continue

            new_lesson = ClassTimeTable.objects.create(
                date=new_date,
                subject=getattr(old, "subject", None),
                teacher=getattr(old, "teacher", None),
                hours=old.hours,
                room=old.room,
                group=getattr(old, "group", None),
                flow=getattr(old, "flow", None),
                branch_id=old.branch_id,
                week=old.week,
            )
            students = list(old.students.all())
            if students:
                new_lesson.students.set(students)

            created_count += 1

            # ---- GroupSubjectsCount (monthly bucket) ----
            group = getattr(old, "group", None)
            if group and old.subject:
                group_subjects = GroupSubjects.objects.filter(
                    group=group, subject=old.subject
                ).first()
                if group_subjects and not GroupSubjectsCount.objects.filter(
                        class_time_table=new_lesson,
                        group_subjects=group_subjects,
                        date=month_date
                ).exists():
                    GroupSubjectsCount.objects.create(
                        class_time_table=new_lesson,
                        group_subjects=group_subjects,
                        date=month_date
                    )
                if group_subjects:
                    monthly_gs_count = GroupSubjectsCount.objects.filter(
                        group_subjects=group_subjects, date=month_date
                    ).count()
                    if group_subjects.count != monthly_gs_count:
                        group_subjects.count = monthly_gs_count
                        group_subjects.save(update_fields=["count"])

            # ---- StudentSubjectCount (monthly bucket) ----
            if students and old.subject:
                gs_for_ss = None
                if group:
                    gs_for_ss = GroupSubjects.objects.filter(
                        group=group, subject=old.subject
                    ).first()

                for student in students:
                    ss_qs = StudentSubject.objects.filter(
                        student=student, subject=old.subject
                    )
                    if gs_for_ss:
                        ss_qs = ss_qs.filter(group_subjects=gs_for_ss)

                    student_subject = ss_qs.first()
                    if not student_subject:
                        continue

                    if not StudentSubjectCount.objects.filter(
                            class_time_table=new_lesson,
                            student_subjects=student_subject,
                            date=month_date
                    ).exists():
                        StudentSubjectCount.objects.create(
                            class_time_table=new_lesson,
                            student_subjects=student_subject,
                            date=month_date
                        )

                    monthly_ss_count = StudentSubjectCount.objects.filter(
                        student_subjects=student_subject, date=month_date
                    ).count()
                    if student_subject.count != monthly_ss_count:
                        student_subject.count = monthly_ss_count
                        student_subject.save(update_fields=["count"])

    print("==========================================================")
    print(f"✅ Created lessons: {created_count}")
    print(f"⏭️ Skipped duplicates: {skipped_count}")

    return f"{created_count} created, {skipped_count} skipped (cloned for next 6 days with monthly counts)"
