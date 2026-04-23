from django.utils.timezone import now
from django.db.models import OuterRef, Exists, Subquery, F
from django.db.models import Count, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from attendances.models import AttendancePerMonth
from students.models import CallLog, DeletedStudent
from lead.models import Lead


class DebtorsAPIView(APIView):
    def get(self, request):
        today = now().date()
        branch_id = request.query_params.get('branch')

        # O'quv yili boshini hisoblash
        if today.month >= 9:  # sentabr-dekabr
            study_year_start = today.replace(month=9, day=1)
        else:  # yanvar-avgust
            study_year_start = today.replace(year=today.year - 1, month=9, day=1)

        # Faqat o'chirilmagan va qarzli studentlarni olish
        base_qs = AttendancePerMonth.objects.filter(
            month_date__gte=study_year_start,
            month_date__lte=today,
            status=False,  # to'lanmagan
            remaining_debt__gt=0  # qarz bor
        ).annotate(
            is_deleted=Exists(
                DeletedStudent.objects.filter(
                    student_id=OuterRef('student_id'),
                    deleted=True
                )
            )
        ).filter(is_deleted=False)

        if branch_id:
            base_qs = base_qs.filter(student__user__branch_id=branch_id)

        # Har bir student uchun oxirgi qo'ng'iroq ma'lumotini olish
        last_call = CallLog.objects.filter(
            student=OuterRef('student')
        ).order_by('-created_at')

        # Studentlar bo'yicha guruhlash va agregatsiya
        debts = (
            base_qs
            .select_related('student__user')
            .values('student')  # Faqat student bo'yicha guruhlash
            .annotate(
                student_name=F('student__user__name'),
                student_surname=F('student__user__surname'),
                student_phone=F('student__user__phone'),
                parents_number=F('student__parents_number'),
                branch_id=F('student__user__branch_id'),
                months_count=Count('id'),  # qarzli oylar soni
                total_debt=Sum('remaining_debt'),  # umumiy qarz
                last_next_call_date=Subquery(last_call.values('next_call_date')[:1]),
            )
            .order_by('-total_debt')  # eng ko'p qarzlidan kamiga
        )

        result = []
        for item in debts:
            next_call = item['last_next_call_date']

            # Agar keyingi qo'ng'iroq sanasi kelajakda bo'lsa, o'tkazib yuborish
            if next_call and next_call > today:
                continue

            months = item['months_count']

            # Rang belgilash: 2+ oy = qizil, 1 oy = sariq
            color = 'red' if months >= 2 else 'yellow'

            result.append({
                "student_id": item['student'],
                "full_name": f"{item['student_name']} {item['student_surname']}",
                "phone": item['student_phone'],
                "parent_phone": item['parents_number'],
                "debt": item['total_debt'] or 0,
                "months_count": months,
                "color": color,
                "branch": item['branch_id']
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
