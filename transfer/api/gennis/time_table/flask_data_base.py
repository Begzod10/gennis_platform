from sqlalchemy import create_engine, Table, MetaData, select

engine = create_engine('postgresql://postgres:123@localhost:5432/gennis')

metadata = MetaData()
metadata.reflect(bind=engine)
group_room_week = Table('group_room_week', metadata, autoload_with=engine)
week = Table('week', metadata, autoload_with=engine)


def get_week(id):
    query = select(week).where(week.c.id == int(id))
    with engine.connect() as conn:
        result = conn.execute(query).fetchone()
    row_dict = dict(zip(week.columns.keys(), result))
    return row_dict


def get_group_room_week():
    list = []
    with engine.connect() as conn:
        result = conn.execute(group_room_week.select()).fetchall()
    for row in result:
        time_table = dict(zip(group_room_week.columns.keys(), row))
        info = {
            'old_id': time_table['id'],
            'group': time_table['group_id'],
            "week": get_week(time_table['week_id'])['eng_name'],
            "room": time_table['room_id'],
            "start_time": time_table['start_time'].strftime("%H:%M"),
            'end_time': time_table['end_time'].strftime("%H:%M"),
            'branch': time_table['location_id']
        }
        print(info)
        list.append(info)
    return list
