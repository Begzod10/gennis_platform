from datetime import date, datetime

from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from overhead.models import Overhead, OverheadType, OverheadTypeLog
from payments.models import PaymentTypes


def _generate_logs_for_month(month: int, year: int, branch_id=None):
    month_date = date(year, month, 1)
    query = OverheadType.objects.filter(
        changeable=False,
        cost__isnull=False,
        deleted=False,
    )
    for ot in query:
        exists = OverheadTypeLog.objects.filter(
            overhead_type=ot,
            date=month_date,
            branch_id=branch_id,
        ).exists()
        if not exists:
            OverheadTypeLog.objects.create(
                overhead_type=ot,
                cost=ot.cost,
                is_paid=False,
                is_prepaid=False,
                branch_id=branch_id,
                date=month_date,
            )


class OverheadTypeLogListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, month, year):
        branch_id = request.query_params.get('branch_id')
        branch_id = int(branch_id) if branch_id else None
        status_param = request.query_params.get('status', 'all')
        month_date = date(year, month, 1)

        _generate_logs_for_month(month, year, branch_id)

        base_qs = OverheadTypeLog.objects.filter(date=month_date, deleted=False)
        if branch_id:
            base_qs = base_qs.filter(branch_id=branch_id)

        qs = base_qs
        if status_param == 'paid':
            qs = qs.filter(is_paid=True)
        elif status_param == 'unpaid':
            qs = qs.filter(is_paid=False)

        total_count = base_qs.count()
        paid_count = base_qs.filter(is_paid=True).count()
        total_sum = base_qs.aggregate(s=Coalesce(Sum('cost'), Value(0)))['s']
        paid_sum = base_qs.filter(is_paid=True).aggregate(s=Coalesce(Sum('cost'), Value(0)))['s']

        return Response({
            'success': True,
            'summary': {
                'total_count': total_count,
                'paid_count': paid_count,
                'unpaid_count': total_count - paid_count,
                'total_sum': total_sum,
                'paid_sum': paid_sum,
                'unpaid_sum': total_sum - paid_sum,
            },
            'data': [log.convert_json() for log in qs.order_by('id')],
        })


class OverheadTypeLogGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, month, year):
        branch_id = request.data.get('branch_id')
        _generate_logs_for_month(month, year, branch_id)
        return Response({'success': True, 'message': 'Loglar yaratildi'})


class OverheadTypeLogPayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        payment_type_id = data.get('payment_type_id')
        branch_id = data.get('branch_id')
        date_str = data.get('date')
        log_id = data.get('log_id')
        overhead_type_id = data.get('overhead_type_id')
        paid_for_month_str = data.get('paid_for_month')

        is_prepaid = paid_for_month_str is not None

        if not is_prepaid and not log_id:
            return Response({'success': False, 'message': 'log_id yoki paid_for_month kerak'}, status=400)
        if is_prepaid and not overhead_type_id:
            return Response({'success': False, 'message': 'paid_for_month bilan overhead_type_id kerak'}, status=400)

        payment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        now = datetime.now()

        if is_prepaid:
            try:
                ot = OverheadType.objects.get(pk=overhead_type_id)
            except OverheadType.DoesNotExist:
                return Response({'success': False, 'message': 'OverheadType topilmadi'}, status=404)

            if ot.changeable:
                return Response({'success': False, 'message': 'Changeable overhead type prepay qilib bolmaydi'}, status=400)

            target_month_dt = datetime.strptime(paid_for_month_str, '%Y-%m')
            target_date = date(target_month_dt.year, target_month_dt.month, 1)

            target_log = OverheadTypeLog.objects.filter(
                overhead_type=ot,
                date=target_date,
            ).first()

            if target_log and target_log.is_paid:
                return Response({'success': False, 'message': "Bu oy allaqachon to'langan"}, status=400)

            if not target_log:
                target_log = OverheadTypeLog.objects.create(
                    overhead_type=ot,
                    cost=ot.cost,
                    branch_id=branch_id,
                    date=target_date,
                )

            overhead = Overhead.objects.create(
                name=ot.name,
                payment_id=payment_type_id,
                created=payment_date,
                price=ot.cost,
                branch_id=branch_id,
                type=ot,
            )

            target_log.is_paid = True
            target_log.is_prepaid = True
            target_log.paid_date = now
            target_log.overhead = overhead
            target_log.save()

            return Response({
                'success': True,
                'message': f"{ot.name} oldindan to'landi",
                'log': target_log.convert_json(),
            })

        else:
            try:
                log = OverheadTypeLog.objects.get(pk=log_id)
            except OverheadTypeLog.DoesNotExist:
                return Response({'success': False, 'message': 'Log topilmadi'}, status=404)

            if log.is_paid:
                return Response({'success': False, 'message': "Bu overhead allaqachon to'langan"}, status=400)

            overhead = Overhead.objects.create(
                name=log.overhead_type.name,
                payment_id=payment_type_id,
                created=payment_date,
                price=log.cost,
                branch_id=branch_id,
                type=log.overhead_type,
            )

            log.is_paid = True
            log.is_prepaid = False
            log.paid_date = now
            log.overhead = overhead
            log.save()

            return Response({
                'success': True,
                'message': f"{log.overhead_type.name} to'landi",
                'log': log.convert_json(),
            })
