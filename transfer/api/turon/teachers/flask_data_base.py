from sqlalchemy import create_engine, Table, MetaData, select

engine = create_engine('postgresql://postgres:123@localhost:5432/pm')

metadata = MetaData()
metadata.reflect(bind=engine)
teachers = Table('teacher', metadata, autoload_with=engine)
teacher_salary_types = Table('teacher_salary_type', metadata, autoload_with=engine)


def get_teachers():
    teacher_list = []
    with engine.connect() as conn:
        results = conn.execute(select(teachers)).mappings().fetchall()
    for row in results:
        teacher = dict(row)
        info = {
            "user": {
                "turon_old_id": teacher['user_id']
            },
            "teacher_salary_type": {
                "turon_old_id": teacher['salary_type']
            },
            "turon_old_id": teacher['id'],
        }
        teacher_list.append(info)
    return teacher_list


def get_teachers_salary_type():
    teacher_salary_type_list = []
    with engine.connect() as conn:
        results = conn.execute(select(teacher_salary_types)).mappings().fetchall()

    for row in results:
        teacher_salary_type = dict(row)
        info = {
            "name": teacher_salary_type['type_name'],
            "salary": teacher_salary_type['salary'],
            "turon_old_id": teacher_salary_type['id'],
        }
        teacher_salary_type_list.append(info)
    return teacher_salary_type_list
