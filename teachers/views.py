from rest_framework.views import APIView
from teachers.models import Teacher
from attendances.models import AttendancePerMonth
from datetime import date
from django.db.models import Sum
from rest_framework.response import Response


def get_remaining_debt_for_student(student_id):
    current_date = date.today()
    remaining_debt_sum = AttendancePerMonth.objects.filter(
        student_id=student_id,
        month_date__lte=current_date
    ).aggregate(total_remaining_debt=Sum('remaining_debt'))
    total_remaining_debt = remaining_debt_sum['total_remaining_debt'] or 0

    return total_remaining_debt


class GetGroupStudents(APIView):

    def get(self, request, pk):
        teachers = Teacher.objects.get(pk=pk)
        datas = []
        for group in teachers.group_set.filter(deleted=False).all():
            for student in group.students.all():
                debt = get_remaining_debt_for_student(student.id)

                datas.append({
                    'id': student.id,
                    'name': student.user.name,
                    'surname': student.user.surname,
                    'number': student.user.phone,
                    'parent_number': student.parents_number,
                    'debt': debt,
                    'group_name': group.name
                })

        return Response(datas)
