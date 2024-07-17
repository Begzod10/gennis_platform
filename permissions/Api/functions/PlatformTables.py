from django.db import connection


def platform_tables():
    with connection.cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()

    table_names = [table[0] for table in tables]
    return table_names
