def check_student_room_teacher(students, teacher, room, hours, week):
    errors = {}
    status = all(not student.class_time_table.filter(hours=hours, week=week).exists() for student in students)
    errors["students"] = [f"{student.user.name} {student.user.surname} o'quvchini darsi bor" for student in students if
                          student.class_time_table.filter(hours=hours, week=week).exists()]

    if teacher.classtimetable_set.filter(hours=hours, week=week).exists():
        status = False
        errors["teacher"] = f"{teacher.user.name} {teacher.user.surname} o'qituvchini darsi bor"
    if not room == None:

        if room.classtimetable_set.filter(hours=hours).exists():
            status = False
            errors["room"] = f"{room.name} xonasida dars bor"

    return status, errors
