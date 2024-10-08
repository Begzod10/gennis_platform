from group.models import Group
from rooms.models import Room


def check_time(group, week_id, room, start_time, end_time):
    status = True
    students = group.students.filter(group_time_table__start_time=start_time,
                                     group_time_table__end_time=end_time,
                                     group_time_table__week=week_id)
    errors = []
    if students:
        status = False
        error_students = [{'id': student.id, 'username': student.user.username, 'name': student.user.name,
                           'surname': student.user.surname}
                          for student in students]

        errors.append({'msg': 'bu voxtda studentlada  dars mavjud', 'students': error_students})
    teacher = group.teacher.filter(group_time_table__start_time__gte=start_time,
                                   group_time_table__end_time=end_time,
                                   group_time_table__week=week_id)
    if teacher:
        status = False
        errors.append({'msg': 'bu voxtda teacherda dars mavjud'})
    if room.grouptimetable_set.all():
        room_time_table = room.grouptimetable_set.filter(week__grouptimetable=week_id,
                                                         start_time__gte=start_time,
                                                         end_time__lte=end_time)
        if room_time_table:
            status = False
            errors.append({'msg': 'bu voxtda roomda dars mavjud'})

    return True if status == True else {'errors': errors}
