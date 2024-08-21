from sqlalchemy import create_engine, Table, MetaData, select

engine = create_engine('postgresql://postgres:123@localhost:5432/gennis')

metadata = MetaData()
metadata.reflect(bind=engine)
students = Table('students', metadata, autoload_with=engine)
phones = Table('phonelist', metadata, autoload_with=engine)
subjects = Table('subjects', metadata, autoload_with=engine)
student_subject = Table('student_subject', metadata, autoload_with=engine)
users = Table('users', metadata, autoload_with=engine)
register_deleted_students = Table('register_deleted_students', metadata, autoload_with=engine)
day_date = Table('calendarday', metadata, autoload_with=engine)
studenthistorygroups = Table('studenthistorygroups', metadata, autoload_with=engine)
studentcharity = Table('studentcharity', metadata, autoload_with=engine)
studentpayments = Table('studentpayments', metadata, autoload_with=engine)


def get_day(id):
    query = select(day_date).where(day_date.c.id == int(id))
    with engine.connect() as conn:
        result = conn.execute(query).fetchone()
    row_dict = dict(zip(day_date.columns.keys(), result))
    return row_dict


def get_student(id):
    query = select(students).where(students.c.id == int(id))
    with engine.connect() as conn:
        result = conn.execute(query).mappings().fetchone()
    if result:
        row_dict = dict(result)
        return row_dict
    return None


def get_user(id):
    query = select(users).where(users.c.id == int(id))
    with engine.connect() as conn:
        result = conn.execute(query).mappings().fetchone()
    if result:
        row_dict = dict(result)
        return row_dict
    return None


def get_subjects_by_student(student_id):
    query = select(student_subject.c.subject_id).where(student_subject.c.student_id == student_id)
    with engine.connect() as conn:
        results = conn.execute(query).mappings().fetchall()

    subject_ids = [row['subject_id'] for row in results]

    if subject_ids:
        query = select(subjects).where(subjects.c.id.in_(subject_ids))
        with engine.connect() as conn:
            subject_results = conn.execute(query).mappings().fetchall()
        subject_list = [dict(row) for row in subject_results]
        return subject_list
    else:
        return []


def get_phones_by_user(id):
    query = select(phones).where(phones.c.user_id == id)
    with engine.connect() as conn:
        results = conn.execute(query).mappings().fetchall()

    list_of_phones = [dict(row) for row in results]

    phone = None
    for number in list_of_phones:
        if number['parent'] is not None and number['parent']:
            phone = number['phone']
    return phone


def get_students():
    student_list = []
    with engine.connect() as conn:
        results = conn.execute(select(students)).mappings().fetchall()

    for row in results:
        student = dict(row)
        phone = get_phones_by_user(student['user_id'])
        shift = 1 if student['morning_shift'] else (2 if student['night_shift'] else 0)

        # Get subjects and rename 'id' to 'old_id'
        subjects = get_subjects_by_student(student['id'])
        for subject in subjects:
            subject['old_id'] = subject.pop('id')  # Correctly renaming 'id' to 'old_id'

        # Format user data as a dictionary with 'old_id'
        user = {"old_id": student['user_id']}

        info = {
            "user": user,  # User should be passed as a dictionary with 'old_id'
            "subject": subjects,  # Make sure this is a list of dicts
            "parents_number": phone,
            "shift": shift,
            "representative_name": student['representative_name'],
            "representative_surname": student['representative_surname'],
            "old_id": student['id'],  # This is the student's id
            "extra_payment": student['extra_payment'],
            "old_money": get_user(student['user_id'])['balance']
        }

        student_list.append(info)

    return student_list


def get_deleted_students():
    student_list = []
    with engine.connect() as conn:
        results = conn.execute(select(register_deleted_students)).mappings().fetchall()
    for row in results:
        student = dict(row)
        year_str = get_day(student['calendar_day'])['date'].strftime(
            '%Y-%m-%d') if get_day(student['calendar_day'])['date'] and get_day(student['calendar_day'])[
            'date'] else None
        student_ = {"old_id": student['student_id']}
        info = {
            "student": student_,
            "comment": student['reason'],
            "created": year_str,
            "old_id": student['id'],
        }
        student_list.append(info)
    return student_list


def get_studenthistorygroups():
    studenthistorygroups_list = []
    with engine.connect() as conn:
        results = conn.execute(select(studenthistorygroups)).mappings().fetchall()
    for row in results:
        studenthistorygroup = dict(row)
        student_id = {"old_id": studenthistorygroup['student_id']}
        teacher_id = {"old_id": studenthistorygroup['teacher_id']}
        group_id = {"old_id": studenthistorygroup['group_id']}
        info = {
            'old_id': studenthistorygroup['id'],
            "student": student_id,
            "teacher": teacher_id,
            "reason": studenthistorygroup['reason'],
            "group": group_id,
            "left_day": studenthistorygroup['left_day'].strftime(
                '%Y-%m-%d') if studenthistorygroup['left_day'] and studenthistorygroup['left_day'] else None,
            "joined_day": studenthistorygroup['joined_day'].strftime(
                '%Y-%m-%d') if studenthistorygroup['left_day'] and studenthistorygroup['left_day'] else None
        }
        studenthistorygroups_list.append(info)
    return studenthistorygroups_list


def get_studentcharity():
    studentcharity_list = []
    with engine.connect() as conn:
        results = conn.execute(select(studentcharity)).mappings().fetchall()

    for row in results:
        student_charity = dict(row)  # Convert row to dictionary
        student_id = {"old_id": student_charity['student_id']}
        group_id = {"old_id": student_charity['group_id']}
        branch_id = {"old_id": student_charity['location_id']}
        info = {
            'old_id': student_charity['id'],
            "student": student_id,
            "group": group_id,
            "charity_sum": student_charity['discount'],
            "added_data": get_day(student_charity['calendar_day'])['date'].strftime("%Y-%m-%d"),
            "branch": branch_id
        }
        studentcharity_list.append(info)
    return studentcharity_list


def get_studentpayments():
    studentpayments_list = []
    with engine.connect() as conn:
        results = conn.execute(select(studentpayments)).mappings().fetchall()
    for row in results:
        studentpayment = dict(row)
        student_id = {"old_id": studentpayment['student_id']}
        branch_id = {"old_id": studentpayment['location_id']}
        payment_type_id = {"old_id": studentpayment['payment_type_id']}
        day_data = get_day(studentpayment['calendar_day'])
        if day_data and 'date' in day_data:
            date_obj = day_data['date']
            year_str = date_obj.strftime('%Y-%m-%d') if hasattr(date_obj, 'strftime') else None
        else:
            year_str = None
        info = {
            "student": student_id,
            "payment_type": payment_type_id,
            "payment_sum": studentpayment['payment_sum'],
            "status": studentpayment['payment'],
            "branch": branch_id,
            "added_data": year_str
        }
        studentpayments_list.append(info)
    return studentpayments_list

