from group.models import Group
from attendances.models import AttendancePerMonth, AttendancePerDay
from students.models import Student
from datetime import datetime


def check_and_create_attendance_per_month(group_id, students, date):
    group = Group.objects.get(pk=group_id)
    teacher = group.teacher.first()
    today = datetime.today()
    month_date = datetime.strptime(f"{today.year}-{today.month}", "%Y-%m")
    day = datetime.strptime(f"{today.year}-{date}", "%Y-%m-%d")
    errors = []
    for student in students:
        current_month_attendance = AttendancePerMonth.objects.get_or_create(month_date=month_date, group_id=group_id,
                                                                            student_id=student['id'],
                                                                            teacher=teacher)
        try:
            attendance_per_day = AttendancePerDay.objects.get(group_id=group_id, teacher=teacher, day=day,
                                                              student_id=student['id'])
            student = Student.objects.get(pk=student['id'])
            errors.append(info={'msg': f'bu kunda {student.user.name} {student.user.surname} davomat qilingan'})
        except AttendancePerDay.DoesNotExist:
            AttendancePerDay.objects.create(month_date=month_date, group_id=group_id,
                                            student_id=student['id'],
                                            teacher=teacher, status=student['status'],
                                            attendance_per_month=current_month_attendance)
