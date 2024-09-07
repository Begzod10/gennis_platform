from time_table.models import TimeTableArchive, WeekDays
from datetime import datetime
from time_table.models import GroupTimeTable
from time_table.functions.creatWeekDays import creat_week_days


def creat_time_table_archive():
    creat_time_table_archive()
    creat_week_days()
    now = datetime.now()
    current_date = datetime.now().date()
    current_time = datetime.now().time().replace(second=0, microsecond=0)
    check_time = datetime.strptime("17:00", "%H:%M").time()
    week_day = WeekDays.objects.get(name_en=now.strftime("%A"))
    time_tables = GroupTimeTable.objects.filter(week=week_day).all()
    if current_time >= check_time:
        for time_table in time_tables:
            created_archive = TimeTableArchive.objects.filter(start_time=time_table.start_time,
                                                              end_time=time_table.end_time, date=current_date,
                                                              group=time_table.group, week=time_table.week,
                                                              room=time_table.room).first()
            if not created_archive:
                TimeTableArchive.objects.create(
                    group=time_table.group, week=time_table.week,
                    room=time_table.room, start_time=time_table.start_time, end_time=time_table.end_time,
                    date=current_date
                )
    return True
