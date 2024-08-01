from group.models import Group
from rooms.models import Room


def check_time(group, week_id, room, start_time, end_time):
    status = True
    students = group.students.filter(group__grouptimetable__start_time__gte=start_time,
                                     group__grouptimetable__end_time=end_time,
                                     group__grouptimetable__week=week_id)
    msg = []
    if students:
        status = False
        error_students = [{'id': student.id, 'username': student.user.username, 'name': student.user.name,
                           'surname': student.user.surname}
                          for student in students]

        msg.append({'msg': 'bu voxtda studentlada dars mavjud', 'students': error_students})
    teacher = group.teacher.filter(group__grouptimetable__start_time__gte=start_time,
                                   group__grouptimetable__end_time=end_time,
                                   group__grouptimetable__week=week_id)
    if teacher:
        status = False
        msg.append({'msg': 'bu voxtda teacherda dars mavjud'})
    if room.grouptimetable_set.all():
        room_time_table = room.grouptimetable_set.filter(week__grouptimetable=week_id,
                                                         start_time__gte=start_time,
                                                         end_time__lte=end_time)
        if room_time_table:
            status = False
            msg.append({'msg': 'bu voxtda roomda dars mavjud'})

    return True if status == True else {'msg': msg}
