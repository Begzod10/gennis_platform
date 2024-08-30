from time_table.models import WeekDays


def creat_week_days():
    weekdays = [{"name": "Monday", "name2": "Dushanba", "order": 1},
                {"name": "Tuesday", "name2": "Seshanba", "order": 2},
                {"name": "Wednesday", "name2": "Chorshanba", "order": 3},
                {"name": "Thursday", "name2": "Payshanba", "order": 4},
                {"name": "Friday", "name2": "Juma", "order": 5}, {"name": "Saturday", "name2": "Shanba", "order": 6},
                {"name": "Sunday", "name2": "Yakshanba", "order": 7}, ]
    [WeekDays.objects.get_or_create(name_uz=weekday['name2'], name_en=weekday['name'], order=weekday['order']) for
     weekday in weekdays]

    return True
