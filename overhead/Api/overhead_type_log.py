from datetime import date, datetime

from django.db import transaction
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from overhead.models import Overhead, OverheadType, OverheadTypeLog, OverheadTypeLogPayment
from overhead.serializers import (
    OverheadTypeLogListResponseSerializer,
    OverheadTypeLogGenerateRequestSerializer, OverheadTypeLogGenerateResponseSerializer,
    OverheadTypeLogPayRequestSerializer, OverheadTypeLogPayResponseSerializer,
)
from payments.models import PaymentTypes


def _generate_logs_for_month(month: int, year: int, branch_id=None):
    month_date = date(year, month, 1)
    query = OverheadType.objects.filter(
        changeable=False,
        cost__isnull=False,
        deleted=False,
    )
    if branch_id is not None:
        query = query.filter(branch_id=branch_id)
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


@extend_schema(
    tags=['Overhead Type Logs'],
    summary='List monthly overhead-type logs',
    description=(
        "Returns reminder logs for fixed overhead types for the given month/year. "
        "Auto-generates missing logs on the first call. Includes a summary block with "
        "paid/unpaid counts and sums."
    ),
    parameters=[
        OpenApiParameter('month', OpenApiTypes.INT, OpenApiParameter.PATH, description='1-12'),
        OpenApiParameter('year', OpenApiTypes.INT, OpenApiParameter.PATH, description='e.g. 2026'),
        OpenApiParameter('branch_id', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False,
                         description='Filter logs by branch'),
        OpenApiParameter('status', OpenApiTypes.STR, OpenApiParameter.QUERY, required=False,
                         description="'paid' | 'unpaid' | 'all' (default: 'all')",
                         enum=['paid', 'unpaid', 'all']),
    ],
    responses={200: OverheadTypeLogListResponseSerializer},
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
            base_qs = base_qs.filter(overhead_type__branch_id=branch_id)

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


@extend_schema(
    tags=['Overhead Type Logs'],
    summary='Manually generate logs for a month',
    description='Creates OverheadTypeLog rows for every fixed overhead type that does not already have one for the given month/year.',
    parameters=[
        OpenApiParameter('month', OpenApiTypes.INT, OpenApiParameter.PATH, description='1-12'),
        OpenApiParameter('year', OpenApiTypes.INT, OpenApiParameter.PATH, description='e.g. 2026'),
    ],
    request=OverheadTypeLogGenerateRequestSerializer,
    responses={200: OverheadTypeLogGenerateResponseSerializer},
)
class OverheadTypeLogGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, month, year):
        branch_id = request.data.get('branch_id')
        _generate_logs_for_month(month, year, branch_id)
        return Response({'success': True, 'message': 'Loglar yaratildi'})


@extend_schema(
    tags=['Overhead Type Logs'],
    summary='Pay an overhead-type log (same-month or prepayment)',
    description=(
        "Creates an Overhead record and marks the corresponding log as paid.\n\n"
        "**Same-month payment:** send `log_id` of the existing OverheadTypeLog.\n\n"
        "**Prepayment for a future month:** send `overhead_type_id` + `paid_for_month` "
        "(format: `'YYYY-MM'`). The system finds or creates the future month's log "
        "and marks it as `is_prepaid=True`. The current month's log stays untouched."
    ),
    request=OverheadTypeLogPayRequestSerializer,
    responses={200: OverheadTypeLogPayResponseSerializer, 400: OverheadTypeLogPayResponseSerializer, 404: OverheadTypeLogPayResponseSerializer},
)
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
            if target_log and target_log.payments.filter(deleted=False).exists():
                return Response({
                    'success': False,
                    'message': "Bu logga qisman to'lovlar mavjud. Prepay qilish uchun avval ularni o'chiring.",
                }, status=400)

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
            if log.payments.filter(deleted=False).exists():
                return Response({
                    'success': False,
                    'message': "Bu logga qisman to'lovlar mavjud. Yangi to'lov uchun /overhead_type_logs/<id>/payments/add dan foydalaning.",
                }, status=400)

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


# ---------------------------------------------------------------------------
# Partial / split payments
# ---------------------------------------------------------------------------

def _recompute_log_paid(log: OverheadTypeLog):
    """Recompute is_paid + paid_date from active payments."""
    active = [p for p in log.payments.all() if not p.deleted]
    paid = sum(p.amount for p in active)
    if paid >= (log.cost or 0) and (log.cost or 0) > 0:
        log.is_paid = True
        latest = max((p.paid_date for p in active if p.paid_date), default=None)
        log.paid_date = latest
    else:
        log.is_paid = False
        log.paid_date = None
    log.save()


@extend_schema(
    tags=['Overhead Type Logs'],
    summary='Add a partial / split payment to an OverheadTypeLog',
    description=(
        "Records one payment installment (cash, click, etc.) against a log.\n"
        "Sum of active payments determines `is_paid` and `payment_status`.\n\n"
        "Body: `payment_type_id`, `amount`, `date` (YYYY-MM-DD), `branch_id`, `note` (optional)."
    ),
)
class OverheadTypeLogPaymentAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, log_id):
        data = request.data
        payment_type_id = data.get('payment_type_id')
        amount = data.get('amount')
        date_str = data.get('date')
        branch_id = data.get('branch_id')
        note = data.get('note')

        if not payment_type_id or amount is None or not date_str or not branch_id:
            return Response({
                'success': False,
                'message': 'payment_type_id, amount, date, branch_id majburiy',
            }, status=400)

        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return Response({'success': False, 'message': "amount butun son bo'lishi kerak"}, status=400)
        if amount <= 0:
            return Response({'success': False, 'message': "amount musbat bo'lishi kerak"}, status=400)

        try:
            payment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'success': False, 'message': 'date format: YYYY-MM-DD'}, status=400)

        created_by = request.user if request.user.is_authenticated else None

        with transaction.atomic():
            try:
                log = OverheadTypeLog.objects.select_for_update().get(pk=log_id)
            except OverheadTypeLog.DoesNotExist:
                return Response({'success': False, 'message': 'Log topilmadi'}, status=404)
            if log.deleted:
                return Response({'success': False, 'message': "Log o'chirilgan"}, status=400)

            existing_paid = log.payments.filter(deleted=False).aggregate(
                s=Coalesce(Sum('amount'), Value(0))
            )['s'] or 0

            if log.overhead_id and existing_paid <= 0:
                return Response({
                    'success': False,
                    'message': "Bu log avval bir martalik to'lov bilan to'langan. Avval u to'lovni bekor qiling.",
                }, status=400)

            cost = log.cost or 0
            if cost <= 0:
                return Response({
                    'success': False, 'message': "Log narxi belgilanmagan",
                }, status=400)
            remaining = max(0, cost - existing_paid)
            if amount > remaining:
                return Response({
                    'success': False,
                    'message': f"To'lov summasi qoldiqdan oshib ketmasligi kerak. Qoldiq: {remaining:,} so'm",
                    'remaining_amount': remaining,
                }, status=400)

            overhead = Overhead.objects.create(
                name=log.overhead_type.name,
                payment_id=payment_type_id,
                created=payment_date,
                price=amount,
                branch_id=branch_id,
                type=log.overhead_type,
            )

            payment = OverheadTypeLogPayment.objects.create(
                overhead_type_log=log,
                payment_type_id=payment_type_id,
                overhead=overhead,
                amount=amount,
                paid_date=datetime.combine(payment_date, datetime.min.time()),
                note=note,
                created_by=created_by,
            )

            _recompute_log_paid(log)

        return Response({
            'success': True,
            'message': f"{amount} so'm to'lov qo'shildi",
            'payment': payment.convert_json(),
            'log': log.convert_json(),
        })


@extend_schema(
    tags=['Overhead Type Logs'],
    summary='Delete (soft) a payment on an OverheadTypeLog',
    description="Soft-deletes the payment row, hard-deletes its accounting Overhead row, then recomputes the log status.",
)
class OverheadTypeLogPaymentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, payment_id):
        log_id = OverheadTypeLogPayment.objects.filter(
            pk=payment_id
        ).values_list('overhead_type_log_id', flat=True).first()
        if log_id is None:
            return Response({'success': False, 'message': 'Payment topilmadi'}, status=404)

        with transaction.atomic():
            log = OverheadTypeLog.objects.select_for_update().filter(pk=log_id).first()
            try:
                payment = OverheadTypeLogPayment.objects.get(pk=payment_id)
            except OverheadTypeLogPayment.DoesNotExist:
                return Response({'success': False, 'message': 'Payment topilmadi'}, status=404)
            if payment.deleted:
                return Response({'success': False, 'message': "Allaqachon o'chirilgan"}, status=400)

            payment.deleted = True
            if payment.overhead_id:
                try:
                    payment.overhead.delete()
                except Overhead.DoesNotExist:
                    pass
                payment.overhead = None
            payment.save()

            _recompute_log_paid(log)

        return Response({
            'success': True,
            'message': "To'lov o'chirildi",
            'log': log.convert_json(),
        })


@extend_schema(
    tags=['Overhead Type Logs'],
    summary='List active payments for a log',
)
class OverheadTypeLogPaymentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, log_id):
        try:
            log = OverheadTypeLog.objects.get(pk=log_id)
        except OverheadTypeLog.DoesNotExist:
            return Response({'success': False, 'message': 'Log topilmadi'}, status=404)
        payments = [p.convert_json() for p in log.payments.all() if not p.deleted]
        return Response({
            'success': True,
            'log_id': log.id,
            'cost': log.cost,
            'paid_amount': log.paid_amount,
            'remaining_amount': log.remaining_amount,
            'payment_status': log.payment_status,
            'payments': payments,
        })


@extend_schema(
    tags=['Overhead Type Logs'],
    summary='Convert a legacy single-pay log into the split-payment model',
    description=(
        "Creates one OverheadTypeLogPayment row from the legacy Overhead's "
        "amount / payment / date, then clears log.overhead so split payments "
        "can be added/removed via the regular endpoints."
    ),
)
class OverheadTypeLogConvertToSplitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, log_id):
        with transaction.atomic():
            log = OverheadTypeLog.objects.select_for_update().filter(pk=log_id).first()
            if not log:
                return Response({'success': False, 'message': 'Log topilmadi'}, status=404)
            if log.deleted:
                return Response({'success': False, 'message': "Log o'chirilgan"}, status=400)
            if log.payments.filter(deleted=False).exists():
                return Response({
                    'success': False,
                    'message': "Bu logda allaqachon split to'lovlar mavjud.",
                }, status=400)
            if not log.overhead_id:
                return Response({
                    'success': False,
                    'message': "Bu log legacy bir martalik to'lov bilan to'lanmagan, konversiya kerak emas.",
                }, status=400)

            legacy = log.overhead
            if not legacy:
                return Response({
                    'success': False,
                    'message': "Legacy Overhead yo'q. log.overhead ni qo'lda tozalang.",
                }, status=400)

            base_date = legacy.created or (log.paid_date.date() if log.paid_date else datetime.now().date())

            payment = OverheadTypeLogPayment.objects.create(
                overhead_type_log=log,
                payment_type_id=legacy.payment_id,
                overhead=legacy,
                amount=legacy.price or log.cost or 0,
                paid_date=datetime.combine(base_date, datetime.min.time()),
                note="Converted from legacy single payment",
                created_by=request.user if request.user.is_authenticated else None,
            )

            log.overhead = None
            log.save(update_fields=['overhead'])
            _recompute_log_paid(log)

        return Response({
            'success': True,
            'message': "Log split-payment formatiga o'tkazildi",
            'payment': payment.convert_json(),
            'log': log.convert_json(),
        })
