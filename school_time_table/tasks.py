from datetime import datetime, timedelta
from django.db import transaction
from celery import shared_task
from .models import ClassTimeTable


@shared_task
def update_school_time_table_task():
    today = datetime.now().date()
    # Monday of the current week
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    print("========== SCHOOL TIMETABLE UPDATE ==========")
    print("Today:", today.strftime("%A"), today)
    print("This week's Monday:", monday.strftime("%A"), monday)
    print("This week's Sunday:", sunday.strftime("%A"), sunday)

    # Always copy forward by 7 days (to next week)
    shift_days = 7
    print(f"Lessons will be shifted by {shift_days} days (to next week).")

    # Get lessons from current week (Mon → Sun)
    source_lessons = ClassTimeTable.objects.filter(
        date__gte=monday,
        date__lte=sunday
    )

    print(f"Found {source_lessons.count()} lessons in this week.")

    if not source_lessons.exists():
        print("❌ Manba haftada dars topilmadi (No lessons found).")
        return "No lessons found"

    new_lessons = []
    skipped_lessons = []
    with transaction.atomic():
        for old in source_lessons:
            new_date = old.date + timedelta(days=shift_days)

            # check for duplicates
            exists = ClassTimeTable.objects.filter(
                date=new_date,
                subject=old.subject,
                teacher=old.teacher,
                # classroom=old.classroom,
                time=old.time
            ).exists()

            if exists:
                print(f"⚠️ Skipped duplicate for {old.subject} | {old.teacher} "
                      f"on {new_date} at {old.time}")
                skipped_lessons.append(old.id)
                continue

            print(f"\n➡️ Cloning lesson ID={old.id} | Date={old.date}")
            students = old.students.all()
            print(f"   - Students: {[s.id for s in students]}")

            # clone
            old.pk = None
            old.date = new_date
            old.save()
            old.students.set(students)

            print(f"   ✅ New lesson created with ID={old.id} | Date={old.date}")
            new_lessons.append(old.id)

    print("=============================================")
    print(f"✅ {len(new_lessons)} lessons copied to next week.")
    print(f"⏭️ {len(skipped_lessons)} lessons skipped (already existed).")

    return f"{len(new_lessons)} new, {len(skipped_lessons)} skipped, from {monday} week"
