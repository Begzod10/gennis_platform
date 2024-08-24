from sqlalchemy import create_engine, Table, MetaData, select

engine = create_engine('postgresql://postgres:123@localhost:5432/gennis')

metadata = MetaData()
metadata.reflect(bind=engine)
groups = Table('groups', metadata, autoload_with=engine)
students = Table('students', metadata, autoload_with=engine)
student_group = Table('student_group', metadata, autoload_with=engine)


def get_student_by_group(group_id):
    query = select(student_group.c.student_id).where(student_group.c.group_id == group_id)
    with engine.connect() as conn:
        results = conn.execute(query).mappings().fetchall()

    student_ids = [row['student_id'] for row in results]

    if student_ids:
        query = select(students).where(students.c.id.in_(student_ids))
        with engine.connect() as conn:
            student_results = conn.execute(query).mappings().fetchall()

        student_list = []
        for row in student_results:
            # student_list.append({'old_id': row['id']})
            student_list.append(row['id'])
        return student_list
    else:
        return []


def get_groups():
    group_list = []
    with engine.connect() as conn:
        result = conn.execute(groups.select()).fetchall()
    for row in result:
        group = dict(zip(groups.columns.keys(), row))
        students = get_student_by_group(group['id'])
        info = {
            'old_id': group['id'],
            'name': group['name'],
            'language': group['education_language'],
            'level': group['level_id'],
            'subject': group['subject_id'],
            'teacher': [group['teacher_id']],
            'students': students,
            'course_types': group['course_type_id'],
            'branch': group['location_id'],
            'system': 1,
            'teacher_salary': group['teacher_salary'],
            'attendance_days': group['attendance_days'],
            'price': group['price'],
            'deleted': group['deleted'],
            'status': group['status']
        }
        group_list.append(info)
    return group_list
