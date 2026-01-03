from celery import shared_task
from datetime import datetime
from .models import Student, DeletedStudent, DeletedNewStudent
from attendances.models import AttendancePerMonth
from students.serializers import get_remaining_debt_for_student


@shared_task
def update_debts_task():
    month_numbers = [9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
    old_months = [9, 10, 11, 12]
    base_year = datetime.now().year  # current academic year

    deleted_student_ids = DeletedStudent.objects.filter(
        student__groups_student__isnull=True,
        deleted=False
    ).values_list('student_id', flat=True)

    deleted_new_student_ids = DeletedNewStudent.objects.values_list('student_id', flat=True)

    active_students = Student.objects.exclude(id__in=deleted_student_ids).exclude(
        id__in=deleted_new_student_ids
    ).filter(groups_student__isnull=False).distinct().order_by('class_number__number')

    print(f"Found {active_students.count()} active students to process...")

    for student in active_students:
        group = student.groups_student.first()
        print(
            f"\nProcessing student {student.id} ({student.user.name} {student.user.surname}) | Group: {group.id if group else 'None'}")

        for month in month_numbers:
            year = base_year if month in old_months else base_year + 1
            month_date = datetime(year, month, 1)

            exist_month = AttendancePerMonth.objects.filter(
                student_id=student.id,
                month_date__year=year,
                month_date__month=month,
                group_id=group.id
            ).first()

            if exist_month:
                print(f"  ✅ Exists: {month_date.strftime('%Y-%m')} (ID: {exist_month.id})")
            else:
                new_record = AttendancePerMonth.objects.create(
                    student_id=student.id,
                    month_date=month_date,
                    total_debt=group.price if group and group.price else 0,
                    payment=0,
                    group_id=group.id,
                    remaining_debt=0
                )
                print(f"  ➕ Created: {month_date.strftime('%Y-%m')} (ID: {new_record.id})")

    print("\n🎉 Debt update task completed.")


@shared_task
def update_student_debt():
    deleted_student_ids = DeletedStudent.objects.filter(
        student__groups_student__isnull=True,
        deleted=False
    ).values_list('student_id', flat=True)

    deleted_new_student_ids = DeletedNewStudent.objects.values_list(
        'student_id', flat=True
    )

    active_students = Student.objects.select_related(
        'user',
        'user__language',
        'class_number'
    ).prefetch_related(
        'user__student_user',
        'groups_student',
        'groups_student__class_number',
        'groups_student__color'
    ).exclude(
        id__in=deleted_student_ids
    ).exclude(
        id__in=deleted_new_student_ids
    ).filter(
        groups_student__isnull=False
    ).distinct().order_by('class_number__number')
    for student in active_students:
        get_remaining_debt_for_student(student.id)


@shared_task()
def update_deleted_students_debts():
    """Create AttendancePerMonth records for deleted students' LAST deletion only"""

    months = [9, 10, 11, 12]  # September to December
    year = 2025

    created_count = 0
    existing_count = 0
    skipped_count = 0

    for month in months:
        month_date = datetime(year, month, 1)
        print(f"\n📅 Processing {month_date.strftime('%Y-%m')}...")

        # Get all students deleted in this month
        deleted_in_month = DeletedStudent.objects.filter(
            deleted=False,
            deleted_date__year=year,
            deleted_date__month=month,
            student__isnull=False,
            group__isnull=False
        ).select_related('student', 'student__user', 'group', 'teacher', 'group__system', 'group__class_number',
                         'group__color')

        # Group by student to find their last deletion
        students_processed = set()

        for deleted_student in deleted_in_month:
            student_id = deleted_student.student.id

            # Skip if we already processed this student this month
            if student_id in students_processed:
                continue

            # Find the LAST (most recent) deletion record for this student
            last_deletion = DeletedStudent.objects.filter(
                student=deleted_student.student,
                deleted=False,
                deleted_date__year=year,
                deleted_date__month=month
            ).order_by('-deleted_date', '-id').first()

            # Only process if this is the last deletion
            if last_deletion.id != deleted_student.id:
                print(
                    f"  ⏭️  Skipping: {deleted_student.student.user.name} {deleted_student.student.user.surname} (not last deletion)")
                skipped_count += 1
                continue

            students_processed.add(student_id)

            # Check if AttendancePerMonth already exists
            exist_month = AttendancePerMonth.objects.filter(
                student=last_deletion.student,
                month_date__year=year,
                month_date__month=month,
                group=last_deletion.group
            ).first()

            if exist_month:
                print(
                    f"  ✅ Exists: {last_deletion.student.user.name} {last_deletion.student.user.surname} - Group: {last_deletion.group.class_number.number}-{last_deletion.group.color.name} (ID: {exist_month.id})")
                existing_count += 1
            else:
                # Create new record for LAST deletion only
                new_record = AttendancePerMonth.objects.create(
                    student=last_deletion.student,
                    teacher=last_deletion.teacher,
                    group=last_deletion.group,
                    month_date=month_date,
                    total_debt=last_deletion.group.price or 0,
                    remaining_debt=last_deletion.group.price or 0,
                    payment=0,
                    status=False,
                    system=last_deletion.group.system,
                    discount=0,
                    discount_percentage=0,
                    present_days=0,
                    absent_days=0,
                    scored_days=0
                )
                print(
                    f"  ➕ Created: {last_deletion.student.user.name} {last_deletion.student.user.surname} - Group: {last_deletion.group.class_number.number}-{last_deletion.group.color.name} - Debt: {new_record.total_debt} (ID: {new_record.id})")
                created_count += 1

    print(f"\n✨ Summary:")
    print(f"   Created: {created_count}")
    print(f"   Already existed: {existing_count}")
    print(f"   Skipped (not last deletion): {skipped_count}")

    return {
        'created': created_count,
        'existing': existing_count,
        'skipped': skipped_count,
        'total_processed': created_count + existing_count + skipped_count
    }
