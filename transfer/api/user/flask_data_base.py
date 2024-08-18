from sqlalchemy import create_engine, Table, MetaData, select

engine = create_engine('postgresql://postgres:123@localhost:5432/gennis')

metadata = MetaData()
metadata.reflect(bind=engine)
users = Table('users', metadata, autoload_with=engine)


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
