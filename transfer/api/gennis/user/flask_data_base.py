from sqlalchemy import create_engine, Table, MetaData, select

engine = create_engine('postgresql://postgres:123@localhost:5432/gennis')

metadata = MetaData()
metadata.reflect(bind=engine)
users = Table('users', metadata, autoload_with=engine)
roles = Table('roles', metadata, autoload_with=engine)
phones = Table('phonelist', metadata, autoload_with=engine)
staff = Table('staff', metadata, autoload_with=engine)
staffsalaries = Table('staffsalaries', metadata, autoload_with=engine)
staffsalary = Table('staffsalary', metadata, autoload_with=engine)
month_date = Table('calendarmonth', metadata, autoload_with=engine)
jobs = Table('roles', metadata, autoload_with=engine)


def get_role(id):
    query = select(roles).where(roles.c.id == int(id))
    with engine.connect() as conn:
        result = conn.execute(query).fetchone()
    if result:
        return dict(zip(roles.columns.keys(), result))
    return None


def get_month(id):
    query = select(month_date).where(month_date.c.id == int(id))
    with engine.connect() as conn:
        result = conn.execute(query).fetchone()
    if result:
        return dict(zip(month_date.columns.keys(), result))
    return None


def get_user(staff_id):
    if not staff_id:
        return None
    query = select(staff).where(staff.c.id == int(staff_id))
    with engine.connect() as conn:
        staff_result = conn.execute(query).mappings().fetchone()
    if staff_result:
        query = select(users).where(users.c.id == int(staff_result['user_id']))
        with engine.connect() as conn:
            user_result = conn.execute(query).mappings().fetchone()
        return user_result
    return None


def get_phones_by_user(id):
    query = select(phones).where(phones.c.user_id == id)
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
    phone = None
    for number in results:
        row_dict = dict(zip(phones.columns.keys(), number))
        if row_dict['personal']:
            phone = row_dict['phone']
            break  # Stop once we find a personal phone number
    return phone


def get_jobs():
    job_list = []
    with engine.connect() as conn:
        result = conn.execute(jobs.select()).fetchall()
    for row in result:
        job = dict(zip(jobs.columns.keys(), row))
        info = {
            "name": job['type_role'],
            "system_id": 1,
            "permissions": []
        }
        job_list.append(info)
    return job_list


def get_salaries():
    salary_list = []
    with engine.connect() as conn:
        result = conn.execute(staffsalary.select()).fetchall()
    for row in result:
        staff = dict(zip(staffsalary.columns.keys(), row))
        month_info = get_month(staff['calendar_month'])
        year_str = month_info['date'].strftime("%Y-%m-%d") if month_info and month_info.get('date') else None
        user_info = get_user(staff['staff_id'])
        if user_info:
            user = user_info['id']
        else:
            user = None
        info = {
            "permission": staff['staff_id'],
            "user": user,
            "date": year_str,
            "total_salary": staff['total_salary'],
            "taken_salary": staff['taken_money'],
            "remaining_salary": staff['remaining_salary'],
            "old_id": staff['id']
        }
        salary_list.append(info)
    return salary_list


def get_staffsalaries():
    salary_list = []
    with engine.connect() as conn:
        result = conn.execute(staffsalaries.select()).fetchall()
    for row in result:
        staff = dict(zip(staffsalaries.columns.keys(), row))
        month_info = get_month(staff['calendar_month'])
        year_str = month_info['date'].strftime("%Y-%m-%d") if month_info and month_info.get('date') else None
        user_info = get_user(staff['staff_id'])
        if user_info:
            user = user_info['id']
        else:
            user = None
        info = {
            "permission": staff['staff_id'],
            "user": user,
            "user_salary": staff['salary_id'],
            "payment_types": staff['payment_type_id'],
            "branch": staff['location_id'],
            "salary": staff['payment_sum'],
            "date": year_str,
            "comment": staff['reason'],
            "deleted": False,
            'old_id': staff['id']
        }
        salary_list.append(info)

    return salary_list


def get_users():
    user_list = []
    with engine.connect() as conn:
        result = conn.execute(users.select()).fetchall()
    for row in result:
        user = dict(zip(users.columns.keys(), row))
        phone = get_phones_by_user(user['id'])
        birth_date = f"{user['born_year'] or '0000'}-{user['born_month'] or '00'}-{user['born_day'] or '00'}"
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
            "birth_date": birth_date,
            "language": user['education_language'],
            "branch": user['location_id'],
            "is_superuser": False,
            "is_staff": False,
        }
        user_list.append(info)
    return user_list


def get_users_jobs():
    user_job_list = []
    with engine.connect() as conn:
        result = conn.execute(users.select()).fetchall()
    for row in result:
        user = dict(zip(users.columns.keys(), row))
        info = {
            "user_id": user['id'],
            "group_id": get_role(user['role_id'])['type_role']
        }
        user_job_list.append(info)
    return user_job_list
