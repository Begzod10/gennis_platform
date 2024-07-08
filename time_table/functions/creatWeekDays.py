from time_table.models import WeekDays


def creat_week_days():
    weekdays = [{"name": "Monday", "order": 1, }, {"name": "Tuesday", "order": 2, },
                {"name": "Wednesday", "order": 3, }, {"name": "Thursday", "order": 4, },
                {"name": "Friday", "order": 5, }, {"name": "Saturday", "order": 6,
                                                   }, {"name": "Sunday", "order": 7, }, ]

    [WeekDays.objects.get_or_create(name=weekday['name'], order=weekday['order']) for weekday in weekdays]

    return True
