from sqlalchemy import create_engine, Table, MetaData, select

engine = create_engine('postgresql://postgres:123@localhost:5432/gennis')

metadata = MetaData()
metadata.reflect(bind=engine)
overheads = Table('overhead', metadata, autoload_with=engine)
day_date = Table('calendarday', metadata, autoload_with=engine)


def get_day(id):
    query = select(day_date).where(day_date.c.id == int(id))
    with engine.connect() as conn:
        result = conn.execute(query).fetchone()
    row_dict = dict(zip(day_date.columns.keys(), result))
    return row_dict


def get_overheads():
    list = []
    with engine.connect() as conn:
        result = conn.execute(overheads.select()).fetchall()
    for row in result:
        overhead = dict(zip(overheads.columns.keys(), row))
        info = {
            "old_id": overhead['id'],
            "name": overhead['item_name'],
            "payment": overhead['payment_type_id'],
            "price": overhead['item_sum'],
            "created": get_day(overhead['calendar_day'])['date'].strftime("%Y-%m-%d"),
            "branch": overhead['location_id']
        }
        list.append(info)
    return list
