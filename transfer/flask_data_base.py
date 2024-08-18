from sqlalchemy import create_engine, Table, MetaData, select

engine = create_engine('postgresql://postgres:123@localhost:5432/gennis')

metadata = MetaData()
metadata.reflect(bind=engine)
attendancehistorystudent = Table('attendancehistorystudent', metadata, autoload_with=engine)
month_date = Table('calendarmonth', metadata, autoload_with=engine)
group = Table('groups', metadata, autoload_with=engine)
users = Table('users', metadata, autoload_with=engine)


def get_month(id):
    query = select(month_date).where(month_date.c.id == int(id))
    with engine.connect() as conn:
        result = conn.execute(query).fetchone()
    row_dict = dict(zip(month_date.columns.keys(), result))
    return row_dict


def get_group(id):
    query = select(group).where(group.c.id == int(id))
    with engine.connect() as conn:
        result = conn.execute(query).fetchone()
    row_dict = dict(zip(group.columns.keys(), result))
    return row_dict


def get_AttendancePerMonths():
    list = []
    with engine.connect() as conn:
        result = conn.execute(attendancehistorystudent.select()).fetchall()
    for row in result:
        row_dict = dict(zip(attendancehistorystudent.columns.keys(), row))
        if row_dict['group_id']:
            info = {
                'old_id': row_dict['id'],
                'student': row_dict['student_id'],
                'teacher': get_group(row_dict['group_id'])['teacher_id'],
                'group': row_dict['group_id'],
                'total_debt': row_dict['total_debt'],
                'ball_percentage': row_dict['average_ball'],
                'remaining_debt': row_dict['remaining_debt'],
                'payment': row_dict['payment'],
                'month_date': get_month(row_dict['calendar_month'])['date'].strftime("%Y-%m-%d"),
                'total_charity': row_dict['total_discount'],
                'system': 1,
                'absent_days': row_dict['absent_days'],
                'scored_days': row_dict['scored_days'],
                'present_days': row_dict['present_days']
            }
            list.append(info)
    return list


def get_users():
    list = []
    with engine.connect() as conn:
        result = conn.execute(users.select()).fetchall()
    for row in result:
        user = dict(zip(users.columns.keys(), row))
        print(user)
        info = {
            'old_id': user['id'],
            "name": user['name'],
            "surname": user['surname'],
            "username": user['username'],
            "father_name": user['father_name'],
            "password": user['password'],
            # "phone": phone,
            "observer": user['observer'],
            "comment": user['comment'],
            "birth_date": f"{user['born_year']}-{user['born_month']}-{user['born_day']}",
            "language": user['education_language'],
            "branch": user['location_id'],
            "is_superuser": False,
            "is_staff": False,
        }
        # list.append(info)
        break
    return list


get_users()
