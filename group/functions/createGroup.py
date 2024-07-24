from students.models import Student
from teachers.models import Teacher
from group.models import Group


def creat_group(students, teacher, name, price, branch, language, teacher_salary, attendance_days, level, subject,
                system, color, class_number):
    group = Group.objects.create(name=name, price=price, branch_id=branch,
                                 language_id=language, teacher_salary=teacher_salary,
                                 attendance_days=attendance_days, status=False, deleted=False,
                                 level_id=level, subject_id=subject, system_id=system,
                                 color_id=color if color else None,
                                 class_number_id=class_number if class_number else None)
    for student in students:
        st = Student.objects.get(pk=student)
        group.students.add(st)
    tch = Teacher.objects.get(pk=teacher)
    group.teacher.add(tch)
    return group
