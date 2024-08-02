from group.models import Group
from rooms.models import Room
from time_table.models import TimeTableArchive, WeekDays
from datetime import datetime


def creat_time_table_archive(group_id, week_id, room_id, start_time, end_time):
    now = datetime.now()
    day = WeekDays.objects.get(pk=week_id)
    given_time = datetime.strptime(start_time, "%H:%M")
    if day.name_en == now.strftime("%A") and now.time() >= given_time.time():
        time_table = TimeTableArchive.objects.filter(date__date=now.date(), group_id=group_id, week_id=week_id,
                                                     room_id=room_id, start_time=start_time, end_time=end_time)
        if not time_table:
            TimeTableArchive.objects.create(
                group_id=group_id, week_id=week_id,
                room_id=room_id, start_time=start_time, end_time=end_time
            )
    return True
