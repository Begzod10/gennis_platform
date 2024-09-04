from sqlalchemy import create_engine, Table, MetaData, select

engine = create_engine('postgresql://postgres:123@localhost:5432/pm')

metadata = MetaData()
metadata.reflect(bind=engine)
class_types = Table('class_type', metadata, autoload_with=engine)
classes = Table('class', metadata, autoload_with=engine)
student_class = Table('student_class', metadata, autoload_with=engine)
teacher_class = Table('teacher_class', metadata, autoload_with=engine)
students = Table('student', metadata, autoload_with=engine)
teachers = Table('teacher', metadata, autoload_with=engine)
rooms = Table('room', metadata, autoload_with=engine)


def get_teacher_by_class(class_id):
    query = select(teacher_class.c.teacher_id).where(teacher_class.c.class_id == class_id)
    with engine.connect() as conn:
        results = conn.execute(query).mappings().fetchall()

    teacher_ids = [row['teacher_id'] for row in results]
    if teacher_ids:
        query = select(teachers).where(teachers.c.id.in_(teacher_ids))
        with engine.connect() as conn:
            subject_results = conn.execute(query).mappings().fetchall()
        subject_list = [dict(row) for row in subject_results]
        subject_list2 = []
        for student in subject_list:
            info = {
                'turon_old_id': student['id']
            }
            subject_list2.append(info)
        return subject_list2
    else:
        return []


def get_student_by_class(class_id):
    query = select(student_class.c.student_id).where(student_class.c.class_id == class_id)
    with engine.connect() as conn:
        results = conn.execute(query).mappings().fetchall()

    student_ids = [row['student_id'] for row in results]

    if student_ids:
        query = select(students).where(students.c.id.in_(student_ids))
        with engine.connect() as conn:
            subject_results = conn.execute(query).mappings().fetchall()
        subject_list = [dict(row) for row in subject_results]
        subject_list2 = []
        for student in subject_list:
            info = {
                'turon_old_id': student['id']
            }
            subject_list2.append(info)
        return subject_list2
    else:
        return []


def get_room():
    room_list = []
    with engine.connect() as conn:
        result = conn.execute(rooms.select()).fetchall()
    for row in result:
        room = dict(zip(rooms.columns.keys(), row))
        info = {
            "turon_old_id": room['id'],
            "name": room['name'],
            "seats_number": room['chair_count'],
            "electronic_board": False,
            "branch": 3,
        }
        room_list.append(info)
    return room_list


def get_class():
    class_list = []
    with engine.connect() as conn:
        result = conn.execute(classes.select()).fetchall()
    for row in result:
        classes_ = dict(zip(classes.columns.keys(), row))
        students_ = get_student_by_class(classes_['id'])
        teachers_ = get_teacher_by_class(classes_['id'])
        info = {
            "turon_old_id": classes_['id'],
            "name": classes_['name'],
            "branch": 3,
            "language": 2,
            "students": students_,
            "teacher": teachers_,
            "system": 4,
            "class_number": classes_['class_number'],
            "color": classes_['color'],
        }
        class_list.append(info)
    return class_list


def get_class_color():
    class_color_list = []
    with engine.connect() as conn:
        result = conn.execute(classes.select()).fetchall()
    for row in result:
        classes_ = dict(zip(classes.columns.keys(), row))
        if classes_['color'] not in [color['name'] for color in class_color_list]:
            info = {
                'old_id': classes_['id'],
                'name': classes_['color'],
            }
            class_color_list.append(info)
    return class_color_list


def get_class_number():
    class_number_list = []
    with engine.connect() as conn:
        result = conn.execute(class_types.select()).fetchall()
    for row in result:
        class_number = dict(zip(class_types.columns.keys(), row))
        info = {
            "old_id": class_number['id'],
            "number": class_number['class_number'],
            "price": class_number['price']
        }
        class_number_list.append(info)
    return class_number_list
