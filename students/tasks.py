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
    months = [9, 10]
    year = datetime.now().year
    for month in months:
        deleted_students = DeletedStudent.objects.filter(
            student__groups_student__isnull=True,
            deleted_date__month__gte=month,
            deleted_date__year=year,
        ).all()
        month_date = datetime(year, month, 1)
        for student in deleted_students:
            if student.group:
                exist_month = AttendancePerMonth.objects.filter(
                    student_id=student.id,
                    month_date__year=year,
                    month_date__month=month,
                    group_id=student.group.id
                ).first()
                if exist_month:
                    print(f"  ✅ Exists: {month_date.strftime('%Y-%m')} (ID: {exist_month.id})")
                else:
                    new_record = AttendancePerMonth.objects.create(
                        student_id=student.id,
                        month_date=month_date,
                        total_debt=student.group.price if student.group and student.group.price else 0,
                        payment=0,
                        group_id=student.group.id,
                        remaining_debt=0
                    )
