from datetime import datetime
import calendar

def old_current_dates(group_id=0, observation=False):
    """
    Django versiyasi: joriy va oldingi oy kunlarini qaytaradi
    """

    today = datetime.now()
    current_year = today.year
    current_month = today.month
    current_day = today.day

    # oldingi oy hisoblash
    old_year = current_year
    old_month = current_month - 1
    if old_month == 0:
        old_month = 12
        old_year -= 1

    # joriy oy kunlari
    number_days = calendar.monthrange(current_year, current_month)[1]
    day_list = [d for d in range(1, number_days + 1) if d <= current_day]

    # oldingi oy kunlari
    number_days_old = calendar.monthrange(old_year, old_month)[1]
    old_days = [d for d in range(1, number_days_old + 1)]

    # faqat observation=True bo‘lsa ikkala oy ham qaytariladi
    if observation:
        data = [
            {
                "name": today.strftime("%b"),   # masalan "Oct"
                "value": f"{current_month:02d}",
                "days": day_list
            },
            {
                "name": datetime(old_year, old_month, 1).strftime("%b"),
                "value": f"{old_month:02d}",
                "days": old_days
            }
        ]
    else:
        data = [
            {
                "name": today.strftime("%b"),
                "value": f"{current_month:02d}",
                "days": day_list
            }
        ]
    return data
from datetime import datetime

def find_calendar_date(date_day=None, date_month=None, date_year=None):
    """
    Flaskdagi Calendar* modellarsiz variant.
    Agar argumentlar berilsa - o'sha sanani qaytaradi,
    bo'lmasa bugungi sanani qaytaradi.
    """
    if date_day and date_month and date_year:
        return datetime(year=date_year, month=date_month, day=date_day)
    return datetime.now()
