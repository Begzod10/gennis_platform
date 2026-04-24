from django.utils.timezone import now
from django.db.models import OuterRef, Exists, Subquery, F
from django.db.models import Count, Sum, Q, Max
from rest_framework.views import APIView
from rest_framework.response import Response
from attendances.models import AttendancePerMonth
from students.models import CallLog, DeletedStudent, Student, DeletedNewStudent
from lead.models import Lead


class DebtorsAPIView(APIView):
    def get(self, request):
        today = now().date()
        branch_id = request.query_params.get('branch')

        if today.month >= 9:
            study_year_start = today.replace(month=9, day=1)
        else:
            study_year_start = today.replace(year=today.year - 1, month=9, day=1)

        deleted_students = DeletedStudent.objects.filter(
            deleted=True
        ).values_list('student_id', flat=True)

        students = Student.objects.filter(
            user__branch_id=branch_id
        ).exclude(
            id__in=deleted_students
        ).select_related('user')

        last_call = CallLog.objects.filter(
            student=OuterRef('pk')
        ).order_by('-created_at')

        students = students.annotate(
            last_next_call_date=Subquery(last_call.values('next_call_date')[:1]),
        )

        result = []
        for student in students:
            next_call = student.last_next_call_date
            if next_call and next_call > today:
                continue

            # Gruppa - GetMonth dagi kabi
            group = student.groups_student.first()
            if group is None:
                history = StudentHistoryGroups.objects.filter(
                    student=student
                ).last()
                if history:
                    group = history.group

            if group is None:
                continue

            attendances = AttendancePerMonth.objects.filter(
                student=student,
                group_id=group.id,
                month_date__gte=study_year_start,
                month_date__lte=today,
                status=False
            )

            months_count = attendances.count()
            if months_count == 0:
                continue

            total_debt = attendances.aggregate(
                total=Sum('remaining_debt')
            )['total'] or 0

            if total_debt <= 0:
                continue

            color = 'red' if months_count >= 2 else 'yellow'

            result.append({
                "student_id": student.id,
                "full_name": f"{student.user.name or ''} {student.user.surname or ''}".strip(),
                "phone": student.user.phone or "",
                "parent_phone": student.parents_number or "",
                "debt": total_debt,
                "months_count": months_count,
                "color": color,
            })

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
