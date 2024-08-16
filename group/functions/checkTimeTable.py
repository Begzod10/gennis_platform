from rooms.models import Room
from students.models import Student


def check_time_table(time_tables, subject):
    status = True
    errors = {
        'rooms': [],
        'students': [],
    }
    for time_table in time_tables:
        print(time_table)
        room = Room.objects.get(id=int(time_table['room']))
        room_time_table = room.grouptimetable_set.filter(week_id=time_table['week'],
                                                         start_time__gte=time_table['start_time'],
                                                         end_time__lte=time_table['end_time']).first()
        if room_time_table:
            status = False
            errors['rooms'].append(f'Bu voxta {room.name} xonasida {room_time_table.group.name}ni  darsi bor')
        students = Student.objects.filter(subject=subject)
        for student in students:
            groups = student.groups_student.all()
            for group in groups:
                student_time_table = group.group_time_table.filter(week_id=time_table['week'],
                                                                   start_time__gte=time_table[
                                                                       'start_time'],
                                                                   end_time__lte=time_table[
                                                                       'end_time']).first()

                if student_time_table:
                    status = False
                    errors['students'].append(
                        f"{student.user.name} {student.user.surname} o'quvchini {group.name} guruhida darsi bor")
    return status, errors
