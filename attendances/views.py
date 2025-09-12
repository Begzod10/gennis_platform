from datetime import datetime

from django.db.models.functions import ExtractYear, ExtractMonth
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F

from collections import defaultdict
import calendar
from datetime import date, timedelta

from attendances.models import AttendancePerMonth, StudentMonthlySummary
from attendances.serializers import AttendancePerMonthSerializer
from students.models import StudentPayment, StudentCharity
from students.serializers import get_remaining_debt_for_student
from .models import AttendancePerDay
from .models import StudentDailyAttendance, GroupMonthlySummary
from .serializers import StudentDailyAttendanceSerializer
from group.models import Group


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


class GroupAttendanceView(APIView):
    def post(self, request, *args, **kwargs):
        group_id = request.data.get("group_id")
        absent_students = request.data.get("absent_students", [])
        day = request.data.get("day")

        if not group_id:
            return Response({"error": "group_id kerak"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"error": "Bunday group mavjud emas"}, status=status.HTTP_404_NOT_FOUND)

        year = day.year if isinstance(day, date) else date.fromisoformat(day).year
        month = day.month if isinstance(day, date) else date.fromisoformat(day).month
        day = day if isinstance(day, date) else date.fromisoformat(day)


        absent_dict = {s["id"]: s.get("reason") for s in absent_students}

        results = []
        for student in group.students.all():
            summary, created = StudentMonthlySummary.objects.get_or_create(
                student=student,
                group=group,
                year=year,
                month=month,
                defaults={"stats": {}}
            )

            reason = absent_dict.get(student.id)
            status_present = student.id not in absent_dict

            daily, created = StudentDailyAttendance.objects.get_or_create(
                monthly_summary=summary,
                day=day,
                defaults={
                    "status": status_present,
                    "reason": reason
                }
            )

            if not created:
                daily.status = status_present
                daily.reason = reason
                daily.save()

            results.append({
                "student_id": student.id,
                "status": daily.status,
                "reason": daily.reason
            })

        return Response({"group_id": group_id, "date": str(day), "attendance": results}, status=status.HTTP_200_OK)


class AttendanceCreateView(generics.CreateAPIView):
    queryset = StudentDailyAttendance.objects.all()
    serializer_class = StudentDailyAttendanceSerializer


class AttendanceDeleteView(generics.DestroyAPIView):
    queryset = StudentDailyAttendance.objects.all()
    serializer_class = StudentDailyAttendanceSerializer
    lookup_field = "id"


def generate_workdays(year, month):
    today = date.today()
    start = date(year, month, 1)
    end_day = today.day if today.year == year and today.month == month else calendar.monthrange(year, month)[1]
    end = date(year, month, end_day)

    days = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            days.append(current.day)
        current += timedelta(days=1)
    return days


class AttendancePeriodsView(APIView):
    def get(self, request):
        group_id = request.query_params.get("group_id")

        summaries = StudentMonthlySummary.objects.filter(group_id=group_id).order_by("year", "month")

        if not summaries.exists():
            today = date.today()
            return Response({
                "group_id": group_id,
                "periods": [
                    {
                        "year": today.year,
                        "months": [
                            {
                                "month": today.month,
                                "days": generate_workdays(today.year, today.month)
                            }
                        ]
                    }
                ]
            })

        periods = {}
        for s in summaries:
            if s.year not in periods:
                periods[s.year] = []
            periods[s.year].append({
                "month": s.month,
                "days": generate_workdays(s.year, s.month)
            })

        result = {
            "group_id": group_id,
            "periods": [
                {"year": year, "months": months}
                for year, months in periods.items()
            ]
        }

        return Response(result, status=status.HTTP_200_OK)


class GroupMonthlyAttendanceView(APIView):
    def get(self, request, *args, **kwargs):
        group_id = request.query_params.get("group_id")
        year = request.query_params.get("year")
        month = request.query_params.get("month")
        print(group_id, year, month)
        if not group_id or not year or not month:
            return Response({"error": "group_id, year va month kerak"}, status=status.HTTP_400_BAD_REQUEST)

        year, month = int(year), int(month)

        _, days_in_month = calendar.monthrange(year, month)
        days_list = list(range(1, days_in_month + 1))

        # summaries = StudentMonthlySummary.objects.filter(group_id=group_id, year=year, month=month)
        # data = [summary.stats for summary in summaries]
        summaries = GroupMonthlySummary.objects.filter(
            group_id=group_id,
            year=year,
            month=month
        ).first()
        data = summaries.stats if summaries else None

        return Response({
            "days": days_list,
            "students": data
        })


class AttendanceDatesView(APIView):
    def get(self, request):
        start_date = date(2025, 9, 1)
        today = date.today()

        dates_by_year = defaultdict(lambda: defaultdict(list))

        current = start_date
        while current <= today:
            if current.weekday() < 5:
                dates_by_year[current.year][current.month].append(current.day)
            current += timedelta(days=1)

        periods = []
        for year, months in dates_by_year.items():
            periods.append({
                "year": year,
                "months": [
                    {"month": m, "days": days}
                    for m, days in sorted(months.items())
                ]
            })

        return Response({"periods": periods}, status=status.HTTP_200_OK)


class BranchDailyStatsView(APIView):
    def get(self, request, branch_id):
        year = int(request.query_params.get("year"))
        month = int(request.query_params.get("month"))
        day = int(request.query_params.get("day"))

        target_date = date(year, month, day)
        groups = Group.objects.filter(branch_id=branch_id).select_related("class_number").order_by(
            "class_number__number")

        branch_present, branch_absent, branch_total = 0, 0, 0
        group_list = []
        for group in groups:
            students = group.students.all()
            records = StudentDailyAttendance.objects.filter(
                monthly_summary__group=group,
                day=target_date
            ).select_related("monthly_summary__student__user")

            rec_map = {r.monthly_summary.student_id: r.status for r in records}

            student_data = []
            present, absent = 0, 0
            for st in students:
                status_val = rec_map.get(st.id, None)
                if status_val is True:
                    present += 1
                    branch_present += 1
                elif status_val is False:
                    absent += 1
                    branch_absent += 1

                student_data.append({
                    "id": st.id,
                    "name": st.user.first_name,
                    "surname": st.user.last_name,
                    "status": status_val
                })
            total_students = students.count()
            branch_total += total_students

            group_list.append({
                "group_id": group.id,
                "group_name": group.name,
                "students": student_data,
                "summary": {
                    "present": present,
                    "absent": absent,
                    "total": students.count()
                }
            })

        return Response({
            "branch_id": branch_id,
            "date": str(target_date),
            "groups": group_list,
            "overall_summary": {
                "present": branch_present,
                "absent": branch_absent,
                "total": branch_total
            }
        }, status=status.HTTP_200_OK)
