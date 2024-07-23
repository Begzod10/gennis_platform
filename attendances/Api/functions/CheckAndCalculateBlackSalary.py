from students.models import Student


def check_and_calculate_black_salary(student):
    if student['debt_status'] > 0:
        return True
    else:
        return False
