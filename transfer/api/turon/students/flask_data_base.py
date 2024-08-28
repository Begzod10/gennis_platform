from sqlalchemy import create_engine, Table, MetaData, select

engine = create_engine('postgresql://postgres:123@localhost:5432/pm')

metadata = MetaData()
metadata.reflect(bind=engine)
students = Table('student', metadata, autoload_with=engine)


def get_students():
    student_list = []
    with engine.connect() as conn:
        results = conn.execute(select(students)).mappings().fetchall()

    for row in results:
        student = dict(row)
        info = {
            "user": {
                "turon_old_id": student['user_id']
            },
            "language_type": student['language_type'],
            "turon_old_id": student['id'],
        }
        student_list.append(info)
    return student_list
