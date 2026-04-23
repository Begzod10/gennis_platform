from django.utils.timezone import now
from django.db.models import OuterRef, Exists, Subquery, F
from django.db.models import Count, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from attendances.models import AttendancePerMonth
from students.models import CallLog, DeletedStudent, Student
from lead.models import Lead


class DebtorsAPIView(APIView):
    def get(self, request):
        from django.db.models import Q, Sum, Count

        today = now().date()
        branch_id = request.query_params.get('branch')

        # O'quv yili boshini hisoblash
        if today.month >= 9:
            study_year_start = today.replace(month=9, day=1)
        else:
            study_year_start = today.replace(year=today.year - 1, month=9, day=1)

        # Bazaviy AttendancePerMonth filtri
        attendance_qs = AttendancePerMonth.objects.filter(
            month_date__gte=study_year_start,
            month_date__lte=today,
            status=False,
            remaining_debt__gt=0
        ).exclude(
            student__id__in=DeletedStudent.objects.filter(
                deleted=True
            ).values_list('student_id', flat=True)
        )

        # Agar branch berilgan bo'lsa
        if branch_id:
            attendance_qs = attendance_qs.filter(student__user__branch_id=branch_id)

        # Noyob student ID larni olish
        student_ids = attendance_qs.values_list('student_id', flat=True).distinct()

        # Studentlarni olish
        students = Student.objects.filter(
            id__in=student_ids
        ).select_related('user')

        result = []

        for student in students:
            # Bu studentning qarzlarini olish
            student_debts = attendance_qs.filter(student_id=student.id)

            # Agregatsiya
            debt_summary = student_debts.aggregate(
                total_debt=Sum('remaining_debt'),
                months_count=Count('id')
            )

            # Oxirgi qo'ng'iroqni tekshirish
            last_call = CallLog.objects.filter(
                student=student
            ).order_by('-created_at').first()

            if last_call and last_call.next_call_date and last_call.next_call_date > today:
                continue

            months = debt_summary['months_count']
            color = 'red' if months >= 2 else 'yellow'

            result.append({
                "student_id": student.id,
                "full_name": f"{student.user.name} {student.user.surname}",
                "phone": student.user.phone,
                "parent_phone": student.parents_number,
                "debt": debt_summary['total_debt'] or 0,
                "months_count": months,
                "color": color,
                "branch": student.user.branch_id
            })

        # Qarz bo'yicha saralash
        result.sort(key=lambda x: x['debt'], reverse=True)

        return Response(result)


class LeadsAPIView(APIView):
    def get(self, request):
        today = now().date()
        branch_id = request.query_params.get('branch')

        base_qs = Lead.objects.filter(
            deleted=False,
            finished=False
        )

        if branch_id:
            base_qs = base_qs.filter(branch_id=branch_id)

        last_call = CallLog.objects.filter(
            lead=OuterRef('pk')
        ).order_by('-created_at')

        leads = base_qs.annotate(
            last_next_call_date=Subquery(last_call.values('next_call_date')[:1]),
            last_called_at=Subquery(last_call.values('created_at')[:1]),
            last_status=Subquery(last_call.values('status')[:1]),
            call_count=Count('calllog'),
        )

        result = []
        for lead in leads:
            next_call = lead.last_next_call_date
            if next_call and next_call > today:
                continue  # hali vaqti kelmagan

            result.append({
                "lead_id": lead.id,
                "full_name": lead.name,
                "phone": lead.phone,
                "branch_id": lead.branch_id,
                "call_count": lead.call_count,
                "last_called_at": lead.last_called_at.isoformat() if lead.last_called_at else None,
                "last_status": lead.last_status,
                "last_next_call_date": next_call.isoformat() if next_call else None,
            })

        return Response(result)
