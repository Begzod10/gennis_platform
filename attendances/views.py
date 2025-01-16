import calendar
from datetime import datetime

from django.db.models.functions import ExtractYear, ExtractMonth
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F

from attendances.models import AttendancePerMonth
from attendances.serializers import AttendancePerMonthSerializer
from students.models import StudentPayment, StudentCharity
from students.serializers import get_remaining_debt_for_student
from .models import AttendancePerDay


# Create your views here.


class DeleteAttendanceMonthApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AttendancePerMonth.objects.all()
    serializer_class = AttendancePerMonthSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"msg": "O'chirildi"}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        attendance = AttendancePerMonth.objects.filter(id=instance.id).first()
        attendance.old_money = attendance.total_debt
        attendance.total_debt = data['total_debt']
        attendance.save()
        sum = get_remaining_debt_for_student(attendance.student_id)
        attendances = AttendancePerMonth.objects.filter(id=instance.id).first()

        return Response(
            {'msg': 'Muvaffaqiyatli o\'zgartirildi', 'total_debt': data['total_debt'],
             'remaining_debt': attendances.payment},
            status=status.HTTP_200_OK)


class AttendanceYearListView(APIView):

    def get(self, request, group_id):
        attendances = AttendancePerMonth.objects.filter(group_id=group_id)

        unique_dates = attendances.annotate(
            year=ExtractYear('month_date'),
        ).values('year').distinct().order_by('year')

        return Response({'dates': list(unique_dates)})

    def post(self, request, group_id):
        data = request.data
        year = data['year']

        attendances = AttendancePerMonth.objects.filter(group_id=group_id, month_date__year=year)

        unique_months = attendances.annotate(
            month=ExtractMonth('month_date')
        ).values('month').distinct().order_by('month')

        month_names = [{'month': month['month'], 'name': calendar.month_name[month['month']]} for month in
                       unique_months]

        return Response({'dates': month_names})


class GroupStudentsForChangeDebtView(APIView):
    def post(self, request, group_id):
        data = request.data
        year = data['year']
        month = data['month']

        attendances = AttendancePerMonth.objects.filter(group_id=group_id, month_date__year=year,
                                                        month_date__month=month)

        data = []
        for attendance in attendances:
            student_payemnt = StudentPayment.objects.filter(
                attendance=attendance, status=True

            ).first()
            data.append({'id': attendance.student_id,
                         'name': attendance.student.user.name,
                         'surname': attendance.student.user.surname,
                         'attendance_id': attendance.id,
                         'total_debt': attendance.total_debt,
                         'remaining_debt': attendance.remaining_debt,
                         'payment': attendance.payment,
                         'discount': student_payemnt.payment_sum if student_payemnt else 0,
                         "reason": StudentCharity.objects.filter(
                             student_id=attendance.student_id).first().name if StudentCharity.objects.filter(
                             student_id=attendance.student_id).first() else None,
                         'charity': attendance.discount
                         })

        return Response({'students': data})


class AttendanceDayAPIView(APIView):
    def get(self, request, group_id):
        current_year = datetime.now().year
        current_month = datetime.now().month

        attendances = AttendancePerDay.objects.filter(
            group_id=group_id
        ).values(
            year=F('day__year'),
            month=F('day__month')
        ).distinct()

        months_data = []
        years = set()

        for record in attendances:
            year = record['year']
            month = f"{record['month']:02d}"
            if not any(month_data['months'][0] == month and month_data['year'] == year for month_data in months_data):
                months_data.append({
                    "months": [month],
                    "year": year
                })
            years.add(year)

        return Response({
            "data": {
                "current_month": current_month,
                "current_year": current_year,
                "months": months_data,
                "years": sorted(list(years))
            }
        })