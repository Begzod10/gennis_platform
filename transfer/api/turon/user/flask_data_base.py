from sqlalchemy import create_engine, Table, MetaData, select

engine = create_engine('postgresql://postgres:123@localhost:5432/pm')

metadata = MetaData()
metadata.reflect(bind=engine)
users = Table('user', metadata, autoload_with=engine)
jobs = Table('job', metadata, autoload_with=engine)
worker = Table('worker', metadata, autoload_with=engine)
students = Table('student', metadata, autoload_with=engine)
teachers = Table('teacher', metadata, autoload_with=engine)

def get_job(id):
    query = select(jobs).where(jobs.c.id == int(id))
    with engine.connect() as conn:
        result = conn.execute(query).fetchone()
    row_dict = dict(zip(jobs.columns.keys(), result))
    return row_dict


def get_jobs():
    job_list = []
    with engine.connect() as conn:
        result = conn.execute(jobs.select()).fetchall()
    for row in result:
        job = dict(zip(jobs.columns.keys(), row))
        info = {
            "name": job['name'],
            "system_id": 2,
            "permissions": []
        }
        job_list.append(info)
    with engine.connect() as conn:
        result = conn.execute(users.select()).fetchall()
    for row in result:
        user = dict(zip(users.columns.keys(), row))
        if user['role'] and user['role'] not in [role['name'] for role in job_list]:
            info = {
                "name": user['role'],
                "system_id": 2,
                "permissions": []
            }
            job_list.append(info)
    return job_list


def get_users_jobs():
    user_job_list = []
    with engine.connect() as conn:
        result = conn.execute(users.select()).fetchall()
    for row in result:
        user = dict(zip(users.columns.keys(), row))
        if user['role']:
            info = {
                "user_id": user['id'],
                "group_id": user['role']
            }
            user_job_list.append(info)
    with engine.connect() as conn:
        result = conn.execute(worker.select()).fetchall()
    for row in result:
        worker_ = dict(zip(worker.columns.keys(), row))
        info = {
            "user_id": worker_['user_id'],
            "group_id": get_job(worker_['job_id'])['name']
        }
        user_job_list.append(info)
    with engine.connect() as conn:
        results = conn.execute(select(students)).mappings().fetchall()
    for row in results:
        student = dict(row)
        info = {
            "user_id": student['user_id'],
            "group_id": 'student'
        }
        user_job_list.append(info)
    with engine.connect() as conn:
        results = conn.execute(select(teachers)).mappings().fetchall()
    for row in results:
        teacher = dict(row)
        info = {
            "user_id": teacher['user_id'],
            "group_id": 'teacher'
        }
        user_job_list.append(info)
    return user_job_list


def get_users():
    user_list = []
    with engine.connect() as conn:
        result = conn.execute(users.select()).fetchall()
    for row in result:
        user = dict(zip(users.columns.keys(), row))
        birth_date = user['birth_date'].strftime("%Y-%m-%d") if user and user.get('birth_date') else None
        if user['username']:
            info = {
                'turon_old_id': user['id'],
                "name": user['name'],
                "surname": user['surname'],
                "username": user['username'],
                "father_name": user['parent_name'],
                "password": user['password'],
                "phone": user['number'],
                "birth_date": birth_date,
                "language": 1,
                "branch": 27,
                "is_superuser": False,
                "is_staff": False,
            }
            user_list.append(info)
    return user_list
