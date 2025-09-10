from datetime import date

from .models import Term


def create_terms_for_year(start_year: int):
    """
    start_year bo'yicha o'quv yilining 4 choragini yaratadi.
    Masalan: 2024 -> academic_year = "2024-2025"
    """
    academic_year = f"{start_year}-{start_year + 1}"

    terms_data = [{"start_date": date(start_year, 9, 2), "end_date": date(start_year, 10, 26), },
        {"start_date": date(start_year, 11, 4), "end_date": date(start_year, 12, 28), },
        {"start_date": date(start_year + 1, 1, 13), "end_date": date(start_year + 1, 3, 22), },
        {"start_date": date(start_year + 1, 3, 31), "end_date": date(start_year + 1, 6, 2), }, ]

    created_terms = []
    for term_data in terms_data:
        term, created = Term.objects.get_or_create(academic_year=academic_year, start_date=term_data["start_date"],
            defaults={"end_date": term_data["end_date"]}, )
        created_terms.append(term)

    return created_terms


def create_multiple_years(start_year: int, count: int = 4):
    """
    Bir nechta o'quv yilini ketma-ket yaratadi.
    start_year: boshlang'ich yil
    count: nechta yil yaratish kerakligi (default=2)
    """
    for i in range(count):
        create_terms_for_year(start_year + i)
