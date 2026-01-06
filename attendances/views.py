import calendar
from collections import defaultdict
from datetime import date, timedelta
from datetime import datetime
from typing import Dict, List, Tuple

from django.db.models import F
from django.db.models.functions import ExtractYear, ExtractMonth
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from attendances.models import AttendancePerMonth, StudentMonthlySummary
from attendances.serializers import AttendancePerMonthSerializer
from group.models import Group
from students.models import StudentPayment, StudentCharity
from students.serializers import get_remaining_debt_for_student
from .models import AttendancePerDay
from .models import StudentDailyAttendance, GroupMonthlySummary
from .serializers import StudentDailyAttendanceSerializer


class ChangeStudentDebitFromClassProfile(generics.RetrieveUpdateDestroyAPIView):
    queryset = AttendancePerMonth.objects.all()
    serializer_class = AttendancePerMonthSerializer
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data

        total_debt = data.get('total_debt')
        if total_debt is None:
            return Response({'error': 'total_debt kiritilishi kerak'}, status=status.HTTP_400_BAD_REQUEST)

        instance.old_money = instance.total_debt
        instance.total_debt = total_debt
        instance.save()

        remaining_debt = get_remaining_debt_for_student(instance.student_id)

        return Response(
            {
                'msg': "Muvaffaqiyatli o'zgartirildi",
                'total_debt': instance.total_debt,
                'remaining_debt': int(instance.total_debt) - int(instance.payment) - int(instance.discount),
            },
            status=status.HTTP_200_OK
        )


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
        print(data)

        total_debt = data.get('total_debt')
        if total_debt is None:
            return Response({'error': 'total_debt kiritilishi kerak'}, status=status.HTTP_400_BAD_REQUEST)
        student_payment = StudentPayment.objects.filter(attendance=instance, status=True).first()

        sum_payment = int(request.data.get('payment_sum'))

        if student_payment is None:
            # Agar mavjud bo'lmasa, yangi payment yaratish
            student_payment = StudentPayment.objects.create(
                attendance=instance,
                payment_sum=sum_payment,
                reason=data.get('reason', ''),
                status=True
            )
            # Attendancedagi summani yangilash
            instance.remaining_debt = instance.total_debt - sum_payment + instance.discount
            instance.payment = sum_payment
            instance.total_charity = sum_payment
        else:
            # Mavjud bo'lsa, summani o'zgartirish
            old_payment = student_payment.payment_sum
            instance.remaining_debt = instance.total_debt - (
                    instance.payment - old_payment) + instance.discount + sum_payment
            instance.payment = instance.payment - old_payment + sum_payment
            instance.total_charity = sum_payment

            # StudentPayment ni yangilash
            student_payment.payment_sum = sum_payment
            student_payment.reason = data.get('reason', student_payment.reason)
            student_payment.save()

        instance.save()

        """Yillik chegirma"""

        discount = int(data['discount'])

        if data.get("persentage"):
            discount_amount = (instance.total_debt * discount) / 100
            instance.discount_percentage = discount
        else:
            discount_amount = discount

        instance.discount = discount_amount
        instance.save()

        StudentCharity.objects.update_or_create(student=instance.student,
                                                defaults={'charity_sum': discount_amount, 'name': data['reason'],
                                                          "group": instance.student.groups_student.first(),
                                                          "branch": instance.student.user.branch})

        instance.old_money = instance.total_debt
        instance.total_debt = total_debt
        instance.save()

        remaining_debt = get_remaining_debt_for_student(instance.student_id)

        return Response({'msg': "Muvaffaqiyatli o'zgartirildi", 'total_debt': instance.total_debt,
                         'discount_percentage': instance.discount_percentage, 'discount': instance.discount,
                         'payment_sum': instance.total_charity, 'reason': data.get('reason'),
                         'remaining_debt': int(instance.total_debt) - int(instance.payment) - int(instance.discount),
                         "persentage": data.get("persentage"), }, status=status.HTTP_200_OK)


class AttendanceYearListView(APIView):

    def get(self, request, group_id):
        attendances = AttendancePerMonth.objects.filter(group_id=group_id)

        unique_dates = attendances.annotate(year=ExtractYear('month_date'), ).values('year').distinct().order_by('year')

        return Response({'dates': list(unique_dates)})

    def post(self, request, group_id):
        data = request.data
        year = data['year']

        attendances = AttendancePerMonth.objects.filter(group_id=group_id, month_date__year=year)

        unique_months = attendances.annotate(month=ExtractMonth('month_date')).values('month').distinct().order_by(
            'month')

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
            student_payemnt = StudentPayment.objects.filter(attendance=attendance, status=True

                                                            ).first()
            data.append({'id': attendance.student_id, 'name': attendance.student.user.name,
                         'surname': attendance.student.user.surname, 'attendance_id': attendance.id,
                         'total_debt': attendance.total_debt, 'remaining_debt': attendance.remaining_debt,
                         'payment': attendance.payment,
                         'discount': student_payemnt.payment_sum if student_payemnt else 0,
                         "reason": StudentCharity.objects.filter(
                             student_id=attendance.student_id).first().name if StudentCharity.objects.filter(
                             student_id=attendance.student_id).first() else None, 'charity': attendance.discount})

        return Response({'students': data})


class AttendanceDayAPIView(APIView):
    def get(self, request, group_id):
        current_year = datetime.now().year
        current_month = datetime.now().month

        attendances = AttendancePerDay.objects.filter(group_id=group_id).values(year=F('day__year'),
                                                                                month=F('day__month')).distinct()

        months_data = []
        years = set()

        for record in attendances:
            year = record['year']
            month = f"{record['month']:02d}"
            if not any(month_data['months'][0] == month and month_data['year'] == year for month_data in months_data):
                months_data.append({"months": [month], "year": year})
            years.add(year)

        return Response({"data": {"current_month": current_month, "current_year": current_year, "months": months_data,
                                  "years": sorted(list(years))}})


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
            summary, created = StudentMonthlySummary.objects.get_or_create(student=student, group=group, year=year,
                                                                           month=month, defaults={"stats": {}})

            reason = absent_dict.get(student.id)
            status_present = student.id not in absent_dict

            daily, created = StudentDailyAttendance.objects.get_or_create(monthly_summary=summary, day=day,
                                                                          defaults={"status": status_present,
                                                                                    "reason": reason})

            if not created:
                daily.status = status_present
                daily.reason = reason
                daily.save()

            results.append({"student_id": student.id, "status": daily.status, "reason": daily.reason})

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


def normalize_periods_ensure_current_and_prev(existing_periods: Dict[int, List[dict]], generate_workdays,
                                              now: datetime, ) -> Dict[int, List[dict]]:
    """
    - Preserves all existing months & days.
    - Merges duplicate entries for the same month (union of days).
    - Ensures both the *current* and *previous* month are present
      in the correct year, adding them if missing.
    """
    if now is None:
        now = datetime.now()
    cur_year, cur_month, cur_day = now.year, now.month, now.day

    # previous month/year
    if cur_month == 1:
        prev_month, prev_year = 12, cur_year - 1
    else:
        prev_month, prev_year = cur_month - 1, cur_year

    must_have: List[Tuple[int, int]] = [(cur_year, cur_month), (prev_year, prev_month)]

    # Fold all existing months, merging duplicates
    folded: Dict[int, Dict[int, set[int]]] = {}  # year -> month -> days(set)
    for raw_year, months in (existing_periods or {}).items():
        year = int(raw_year)
        ymap = folded.setdefault(year, {})
        for item in months or []:
            m = int(item["month"])
            days = set(int(d) for d in item.get("days", []))
            ymap[m] = ymap.get(m, set()).union(days)

    # Ensure required months exist
    for y, m in must_have:
        ymap = folded.setdefault(y, {})
        if m not in ymap:
            ymap[m] = set(generate_workdays(y, m))

    if cur_year in folded and cur_month in folded[cur_year]:

        current_days = {int(d) for d in folded[cur_year][cur_month]}
        folded[cur_year][cur_month] = current_days & set(range(1, cur_day + 1))
    else:
        # if you add the current month here, cap it immediately too
        folded.setdefault(cur_year, {})
        folded[cur_year][cur_month] = set(generate_workdays(cur_year, cur_month)) & set(range(1, cur_day + 1))

    # Back to the target structure (sorted)
    normalized: Dict[int, List[dict]] = {}
    for y, ymap in folded.items():
        normalized[y] = [{"month": m, "days": sorted(days)} for m, days in sorted(ymap.items(), key=lambda kv: kv[0])]

    return normalized


class AttendancePeriodsView(APIView):
    def get(self, request):
        group_id = request.query_params.get("group_id")

        summaries = StudentMonthlySummary.objects.filter(group_id=group_id).order_by("year", "month").distinct()

        if not summaries.exists():
            today = date.today()
            return Response({"group_id": group_id, "periods": [{"year": today.year,
                                                                "months": [{"month": today.month,
                                                                            "days": generate_workdays(today.year,
                                                                                                      today.month)}]}]})

        periods = {}
        now = datetime.now()
        normalized = normalize_periods_ensure_current_and_prev(periods, generate_workdays, now)

        result = {"group_id": group_id,
                  "periods": [{"year": y, "months": normalized[y]} for y in sorted(normalized.keys())]}
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

        days_list = [day for day in range(1, days_in_month + 1) if calendar.weekday(year, month, day) != 6]

        summaries = GroupMonthlySummary.objects.filter(group_id=group_id, year=year, month=month).first()
        data = summaries.stats if summaries else None

        return Response({"days": days_list, "students": data})


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
            periods.append({"year": year, "months": [{"month": m, "days": days} for m, days in sorted(months.items())]})

        return Response({"periods": periods}, status=status.HTTP_200_OK)


class BranchDailyStatsView(APIView):
    def get(self, request, branch_id):
        year = int(request.query_params.get("year"))
        month = int(request.query_params.get("month"))
        day = int(request.query_params.get("day"))

        target_date = date(year, month, day)

        groups = Group.objects.filter(branch_id=branch_id, deleted=False).select_related("class_number").order_by(

            "class_number__number")

        branch_present, branch_absent, branch_total = 0, 0, 0
        group_list = []
        for group in groups:
            students = group.students.all()
            records = StudentDailyAttendance.objects.filter(monthly_summary__group=group,
                                                            day=target_date).select_related(
                "monthly_summary__student__user")

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

                student_data.append(
                    {"id": st.id, "name": st.user.name, "surname": st.user.surname, "status": status_val})
            total_students = students.count()
            branch_total += total_students

            group_list.append({"group_id": group.id, "group_name": group.name, "students": student_data,
                               "summary": {"present": present, "absent": absent, "total": students.count()}})

        return Response({"branch_id": branch_id, "date": str(target_date), "groups": group_list,
                         "overall_summary": {"present": branch_present, "absent": branch_absent,
                                             "total": branch_total}},
                        status=status.HTTP_200_OK)
