from sqlalchemy import create_engine, Table, MetaData, select

engine = create_engine('postgresql://postgres:123@localhost:5432/gennis')

metadata = MetaData()
metadata.reflect(bind=engine)
users = Table('users', metadata, autoload_with=engine)
phones = Table('phonelist', metadata, autoload_with=engine)
staffsalaries = Table('staffsalaries', metadata, autoload_with=engine)
staffsalary = Table('staffsalary', metadata, autoload_with=engine)


def get_phones_by_user(id):
    query = select(phones).where(phones.c.user_id == id)
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
    list = []
    for number in results:
        row_dict = dict(zip(phones.columns.keys(), number))
        list.append(row_dict)
    phone = 0
    for number in list:
        if number['personal'] != None and number['personal'] == True:
            phone = number['phone']
    return phone


def get_salaries():
    list = []
    with engine.connect() as conn:
        result = conn.execute(staffsalaries.select()).fetchall()
    for row in result:
        user = dict(zip(users.columns.keys(), row))
        phone = get_phones_by_user(user['id'])
        # info = {
        #     "permission": staff.staff_id,
        #     "user": staff.staff.user.id,
        #     "user_salary": staff.salary_id,
        #     "payment_types": staff.payment_type_id,
        #     "branch": staff.location_id,
        #     "salary": staff.payment_sum,
        #     "date": year_str,
        #     "comment": staff.reason,
        #     "deleted": False,
        #     'old_id': staff.id
        # }
        # print(info)
        # list.append(info)
        break
    return list


def get_users():
    list = []
    with engine.connect() as conn:
        result = conn.execute(users.select()).fetchall()
    for row in result:
        user = dict(zip(users.columns.keys(), row))
        phone = get_phones_by_user(user['id'])
        info = {
            'old_id': user['id'],
            "name": user['name'],
            "surname": user['surname'],
            "username": user['username'],
            "father_name": user['father_name'],
            "password": user['password'],
            "phone": phone,
            "observer": user['observer'],
            "comment": user['comment'],
            "birth_date": f"{user['born_year']}-{user['born_month']}-{user['born_day']}",
            "language": user['education_language'],
            "branch": user['location_id'],
            "is_superuser": False,
            "is_staff": False,
        }
        list.append(info)
    return list
