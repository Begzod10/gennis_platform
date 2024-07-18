from students.models import Student
from teachers.models import Teacher
from group.models import Group


def creat_group(students, teacher, name, price, branch, language, teacher_salary, attendance_days, level, subject,
                system):
    group = Group.objects.create(name=name, price=price, branch=branch,
                                 language=language, teacher_salary=teacher_salary,
                                 attendance_days=attendance_days, status=False, deleted=False,
                                 level=level, subject=subject, system=system)
    for student in students:
        st = Student.objects.get(pk=student)
        group.students.add(st)
    tch = Teacher.objects.get(pk=teacher)
    group.teacher.add(tch)
    return group
