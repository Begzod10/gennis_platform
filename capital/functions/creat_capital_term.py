from datetime import datetime

from capital.models import CapitalTerm, Capital


# def creat_capital_term(capital):
#
#     today = datetime.now()
#     year = today.year
#     month = today.month
#     day = today.day
#     number = len(CapitalTerm.objects.get(capital_id=capital['id']).all())
#     capital_year = capital.added_date.year
#     capital_month = capital.added_date.month + number + 1
#     while capital_month > 12:
#         capital_year += 1
#         capital_month - 12
#     down_cost = capital.price / (12 * capital.term)
#     if year == capital_year and month == capital_month and day >= capital.added_date.day:
#         capital_term = CapitalTerm.objects.filter(capital=capital, month_date__year=year, month_date__month=month)
#         if not capital_term:
#             CapitalTerm.objects.create(
#                 down_cost=down_cost,
#                 capital=capital,
#             )
#             capital.total_down_cost -= down_cost
#             capital.save()
#     return True


def creat_capital_term(capital):
    today = datetime.now()
    year = today.year
    month = today.month
    day = today.day
    number_of_terms = CapitalTerm.objects.filter(capital_id=capital['id']).count()
    capital = Capital.objects.get(id=capital['id'])
    capital_year = capital.added_date.year
    capital_month = capital.added_date.month + number_of_terms + 1
    while capital_month > 12:
        capital_year += 1
        capital_month -= 12
    down_cost = capital.price / (12 * capital.term)
    if year == capital_year and month == capital_month and day >= capital.added_date.day:
        capital_term = CapitalTerm.objects.filter(capital=capital, month_date__year=year,
                                                  month_date__month=month).first()
        if not capital_term:
            CapitalTerm.objects.create(
                down_cost=down_cost,
                capital=capital,
            )
            capital.total_down_cost -= down_cost
            capital.save()

    return True
