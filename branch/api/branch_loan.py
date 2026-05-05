from collections import defaultdict
from datetime import datetime

from django.db import transaction as db_transaction
from django.db.models import Q, Sum
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
)
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from branch.filters import BranchLoanFilter
from branch.models import Branch, BranchLoan, BranchTransaction
from branch.serializers import (
    BranchLoanCancelRequestSerializer,
    BranchLoanCreateRequestSerializer,
    BranchLoanErrorResponseSerializer,
    BranchLoanItemSerializer,
    BranchLoanListSerializer,
    BranchLoanOutstandingResponseSerializer,
    BranchLoanPaginatedListResponseSerializer,
    BranchLoanRepayRequestSerializer,
    BranchLoanSimpleResponseSerializer,
    BranchLoanUpdateRequestSerializer,
)
from payments.models import PaymentTypes
from permissions.response import CustomPagination, QueryParamFilterMixin
from user.models import CustomUser


_LOAN_EXAMPLE = {
    "id": 51,
    "branch_id": 9,
    "counterparty": {"id": 42, "name": "Ali", "surname": "Valiyev", "phone": "+998901112233"},
    "direction": "out",
    "principal_amount": 1000000,
    "paid_total": 600000,
    "remaining_amount": 400000,
    "is_settled": False,
    "issued_date": "2026-04-30",
    "due_date": "2026-05-30",
    "settled_date": None,
    "reason": "Vaqtinchalik qarz",
    "notes": None,
    "status": "active",
    "cancelled_reason": None,
    "management_id": None,
}


def _resolve_counterparty(data):
    cp_id = data.get('counterparty_id')
    cp_name = data.get('counterparty_name')

    if cp_id and cp_name:
        return None, "counterparty_id va counterparty_name ikkalasini birga yuborish mumkin emas"
    if not cp_id and not cp_name:
        return None, "counterparty_id yoki counterparty_name kerak"

    if cp_id:
        cp = CustomUser.objects.filter(id=cp_id).first()
        if not cp:
            return None, "Foydalanuvchi topilmadi"
        return {'user': cp}, None
    return {
        'name': cp_name,
        'surname': data.get('counterparty_surname'),
        'phone': data.get('counterparty_phone'),
    }, None


@extend_schema(
    tags=['Branch Loans'],
    summary='Qarz yaratish (avtomatik tranzaksiya bilan)',
    description=(
        "Yangi qarz va birinchi tranzaksiya (chiqim/kirim) atomik ravishda yaratiladi. "
        "`direction='out'` — filial qarz berdi, `direction='in'` — filial qarz oldi."
    ),
    request=BranchLoanCreateRequestSerializer,
    responses={
        201: BranchLoanSimpleResponseSerializer,
        400: BranchLoanErrorResponseSerializer,
        404: BranchLoanErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Filial qarzga berdi',
            value={
                "branch_id": 9,
                "direction": "out",
                "principal_amount": 1000000,
                "issued_date": "2026-04-30",
                "due_date": "2026-05-30",
                "payment_type_id": 1,
                "counterparty_id": 42,
                "reason": "Vaqtinchalik qarz",
            },
            request_only=True,
        ),
        OpenApiExample(
            'Filial qarz oldi (tashqi shaxsdan)',
            value={
                "branch_id": 9,
                "direction": "in",
                "principal_amount": 1000000,
                "issued_date": "2026-04-30",
                "payment_type_id": 1,
                "counterparty_name": "Akmal",
                "counterparty_surname": "Sa'dullayev",
                "counterparty_phone": "+998935556677",
                "reason": "Mahsulot uchun avans",
            },
            request_only=True,
        ),
        OpenApiExample(
            'Muvaffaqiyatli javob',
            value={"success": True, "message": "Qarz yaratildi", "data": _LOAN_EXAMPLE},
            response_only=True,
            status_codes=['201'],
        ),
    ],
)
class BranchLoanCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        for field in ('branch_id', 'direction', 'principal_amount', 'issued_date', 'payment_type_id'):
            if data.get(field) in (None, ''):
                return Response(
                    {'success': False, 'message': f"{field} kerak"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        direction = str(data.get('direction')).strip().lower()
        if direction not in ('out', 'in'):
            return Response(
                {'success': False, 'message': "direction 'out' yoki 'in' bo'lishi kerak"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            principal = int(data.get('principal_amount'))
        except (TypeError, ValueError):
            return Response(
                {'success': False, 'message': "principal_amount noto'g'ri"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if principal <= 0:
            return Response(
                {'success': False, 'message': "principal_amount > 0 bo'lishi kerak"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            issued_date = datetime.strptime(data.get('issued_date'), '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return Response(
                {'success': False, 'message': "issued_date YYYY-MM-DD formatida bo'lishi kerak"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            except (TypeError, ValueError):
                return Response(
                    {'success': False, 'message': "due_date YYYY-MM-DD formatida bo'lishi kerak"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not Branch.objects.filter(id=data['branch_id']).exists():
            return Response(
                {'success': False, 'message': 'Filial topilmadi'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not PaymentTypes.objects.filter(id=data['payment_type_id']).exists():
            return Response(
                {'success': False, 'message': "To'lov turi topilmadi"},
                status=status.HTTP_404_NOT_FOUND,
            )

        cp, err = _resolve_counterparty(data)
        if err:
            return Response({'success': False, 'message': err}, status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            loan = BranchLoan.objects.create(
                branch_id=data['branch_id'],
                counterparty=cp.get('user') if cp.get('user') else None,
                counterparty_name=cp.get('name'),
                counterparty_surname=cp.get('surname'),
                counterparty_phone=cp.get('phone'),
                direction=direction,
                principal_amount=principal,
                issued_date=issued_date,
                due_date=due_date,
                reason=data.get('reason'),
                notes=data.get('notes'),
                created_by=request.user if request.user.is_authenticated else None,
            )

            BranchTransaction.objects.create(
                amount=principal,
                is_give=(direction == 'out'),
                reason=data.get('reason'),
                person=cp.get('user') if cp.get('user') else None,
                person_name=cp.get('name'),
                person_surname=cp.get('surname'),
                person_phone=cp.get('phone'),
                payment_type_id=data['payment_type_id'],
                branch_id=data['branch_id'],
                date=issued_date,
                loan=loan,
                created_by=request.user if request.user.is_authenticated else None,
            )

        return Response(
            {'success': True, 'message': 'Qarz yaratildi', 'data': loan.convert_json(with_transactions=True)},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=['Branch Loans'],
    summary='Qarzlar ro\'yxati (paginated)',
    parameters=[
        OpenApiParameter('branch', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
        OpenApiParameter('status', OpenApiTypes.STR, OpenApiParameter.QUERY, required=False,
                         enum=['active', 'settled', 'cancelled']),
        OpenApiParameter('direction', OpenApiTypes.STR, OpenApiParameter.QUERY, required=False,
                         enum=['out', 'in']),
        OpenApiParameter('counterparty', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
        OpenApiParameter('search', OpenApiTypes.STR, OpenApiParameter.QUERY, required=False,
                         description="reason, notes, counterparty ism/familiya bo'yicha"),
        OpenApiParameter('limit', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
        OpenApiParameter('offset', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
    ],
    responses={200: BranchLoanPaginatedListResponseSerializer},
)
class BranchLoanListView(QueryParamFilterMixin, generics.ListAPIView):
    filter_mappings = {
        'branch': 'branch_id',
    }
    permission_classes = [IsAuthenticated]
    search_fields = ['reason', 'notes', 'counterparty__name', 'counterparty__surname',
                     'counterparty_name', 'counterparty_surname']

    queryset = BranchLoan.objects.filter(deleted=False).select_related('branch', 'counterparty')
    serializer_class = BranchLoanListSerializer
    filterset_class = BranchLoanFilter
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]

    def list(self, request, *args, **kwargs):
        self.filter_conditions = Q()
        queryset = self.filter_queryset(self.get_queryset()).order_by('-issued_date', '-id')

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        active_qs = queryset.filter(status='active')
        out_qs = queryset.filter(direction='out')
        in_qs = queryset.filter(direction='in')
        active_total = active_qs.aggregate(total=Sum('principal_amount'))['total'] or 0
        out_total = out_qs.aggregate(total=Sum('principal_amount'))['total'] or 0
        in_total = in_qs.aggregate(total=Sum('principal_amount'))['total'] or 0

        return self.get_paginated_response({
            'data': serializer.data,
            'totalCount': [
                {"name": "Total Loans", "totalPayment": queryset.aggregate(t=Sum('principal_amount'))['t'] or 0,
                 "totalPaymentCount": queryset.count(), "type": "amount"},
                {"name": "Active", "totalPayment": active_total, "totalPaymentCount": active_qs.count(),
                 "type": "active"},
                {"name": "Lent (out)", "totalPayment": out_total, "totalPaymentCount": out_qs.count(),
                 "type": "out"},
                {"name": "Borrowed (in)", "totalPayment": in_total, "totalPaymentCount": in_qs.count(),
                 "type": "in"},
            ],
        })


@extend_schema(
    tags=['Branch Loans'],
    summary='Qarz tafsiloti (tranzaksiyalar bilan)',
    responses={200: BranchLoanSimpleResponseSerializer, 404: BranchLoanErrorResponseSerializer},
)
class BranchLoanDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        loan = BranchLoan.objects.filter(id=pk, deleted=False).select_related('branch', 'counterparty').first()
        if not loan:
            return Response({'success': False, 'message': 'Qarz topilmadi'},
                            status=status.HTTP_404_NOT_FOUND)
        return Response({'success': True, 'message': 'OK', 'data': loan.convert_json(with_transactions=True)})


@extend_schema(
    tags=['Branch Loans'],
    summary='Qarz shartlarini yangilash (due_date / reason / notes)',
    request=BranchLoanUpdateRequestSerializer,
    responses={200: BranchLoanSimpleResponseSerializer, 404: BranchLoanErrorResponseSerializer},
)
class BranchLoanUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        loan = BranchLoan.objects.filter(id=pk, deleted=False).first()
        if not loan:
            return Response({'success': False, 'message': 'Qarz topilmadi'},
                            status=status.HTTP_404_NOT_FOUND)
        if loan.status == 'cancelled':
            return Response({'success': False, 'message': "Bekor qilingan qarzni o'zgartirib bo'lmaydi"},
                            status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        if 'due_date' in data:
            if data['due_date']:
                try:
                    loan.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
                except (TypeError, ValueError):
                    return Response({'success': False, 'message': "due_date YYYY-MM-DD"},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                loan.due_date = None
        if 'reason' in data:
            loan.reason = data['reason']
        if 'notes' in data:
            loan.notes = data['notes']

        loan.save()
        return Response({'success': True, 'message': 'Yangilandi',
                         'data': loan.convert_json(with_transactions=True)})


@extend_schema(
    tags=['Branch Loans'],
    summary='Qarzni qaytarish (yoki bo\'lib-bo\'lib to\'lash)',
    description=(
        "Tranzaksiya yaratiladi. Asl qarz `direction` ga teskari yo'nalishda. "
        "Agar jami to'lov principal_amount ga yetsa yoki o'tib ketsa — "
        "qarz status `settled` ga o'tadi."
    ),
    request=BranchLoanRepayRequestSerializer,
    responses={
        201: BranchLoanSimpleResponseSerializer,
        400: BranchLoanErrorResponseSerializer,
        404: BranchLoanErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Birinchi qism',
            value={"amount": 300000, "payment_type_id": 1, "date": "2026-05-05"},
            request_only=True,
        ),
    ],
)
class BranchLoanRepayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        loan = BranchLoan.objects.filter(id=pk, deleted=False).first()
        if not loan:
            return Response({'success': False, 'message': 'Qarz topilmadi'},
                            status=status.HTTP_404_NOT_FOUND)
        if loan.status == 'cancelled':
            return Response({'success': False, 'message': "Bekor qilingan qarzga to'lov qilib bo'lmaydi"},
                            status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        try:
            amount = int(data.get('amount'))
        except (TypeError, ValueError):
            return Response({'success': False, 'message': "amount kerak"},
                            status=status.HTTP_400_BAD_REQUEST)
        if amount <= 0:
            return Response({'success': False, 'message': "amount > 0 bo'lishi kerak"},
                            status=status.HTTP_400_BAD_REQUEST)

        payment_type_id = data.get('payment_type_id')
        if not payment_type_id or not PaymentTypes.objects.filter(id=payment_type_id).exists():
            return Response({'success': False, 'message': "To'lov turi topilmadi"},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
        except (TypeError, ValueError):
            return Response({'success': False, 'message': "date YYYY-MM-DD"},
                            status=status.HTTP_400_BAD_REQUEST)

        with db_transaction.atomic():
            BranchTransaction.objects.create(
                amount=amount,
                is_give=(loan.direction == 'in'),  # repayment is opposite direction of loan
                reason=data.get('reason'),
                person=loan.counterparty,
                person_name=loan.counterparty_name,
                person_surname=loan.counterparty_surname,
                person_phone=loan.counterparty_phone,
                payment_type_id=payment_type_id,
                branch_id=loan.branch_id,
                date=date,
                loan=loan,
                created_by=request.user if request.user.is_authenticated else None,
            )
            loan.recompute_status()
            loan.refresh_from_db()

        return Response(
            {'success': True, 'message': "To'lov qabul qilindi",
             'data': loan.convert_json(with_transactions=True)},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=['Branch Loans'],
    summary='Qarzni bekor qilish',
    description="Holatni `cancelled` ga o'tkazadi. Tranzaksiyalar saqlanadi (audit uchun).",
    request=BranchLoanCancelRequestSerializer,
    responses={
        200: BranchLoanSimpleResponseSerializer,
        400: BranchLoanErrorResponseSerializer,
        404: BranchLoanErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Sabab bilan bekor qilish',
            value={"cancelled_reason": "Kelishuv buzildi"},
            request_only=True,
        ),
    ],
)
class BranchLoanCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        loan = BranchLoan.objects.filter(id=pk, deleted=False).first()
        if not loan:
            return Response({'success': False, 'message': 'Qarz topilmadi'},
                            status=status.HTTP_404_NOT_FOUND)

        reason = (request.data.get('cancelled_reason') or '').strip()
        if not reason:
            return Response({'success': False, 'message': "cancelled_reason kerak"},
                            status=status.HTTP_400_BAD_REQUEST)

        loan.status = 'cancelled'
        loan.cancelled_reason = reason
        loan.settled_date = None
        loan.save(update_fields=['status', 'cancelled_reason', 'settled_date', 'updated_at'])

        return Response({'success': True, 'message': "Qarz bekor qilindi",
                         'data': loan.convert_json(with_transactions=True)})


@extend_schema(
    tags=['Branch Loans'],
    summary='Faol qarzlar — har bir kontragent bo\'yicha qoldiq',
    description="Faol (`status='active'`) qarzlar kontragent bo'yicha guruhlangan ro'yxati.",
    parameters=[
        OpenApiParameter('branch', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
        OpenApiParameter('direction', OpenApiTypes.STR, OpenApiParameter.QUERY, required=False,
                         enum=['out', 'in']),
    ],
    responses={200: BranchLoanOutstandingResponseSerializer},
)
class BranchLoanOutstandingView(QueryParamFilterMixin, APIView):
    filter_mappings = {
        'branch': 'branch_id',
    }
    permission_classes = [IsAuthenticated]

    def get(self, request):
        self.filter_conditions = Q()
        qs = BranchLoan.objects.filter(deleted=False, status='active').select_related(
            'counterparty', 'branch',
        )

        # Manual filter — QueryParamFilterMixin's filter_queryset expects a queryset
        # passed to it, so we apply branch & direction by hand here.
        branch_param = request.query_params.get('branch')
        if branch_param:
            try:
                qs = qs.filter(branch_id=int(branch_param))
            except (TypeError, ValueError):
                return Response({'success': False, 'message': 'branch noto\'g\'ri'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            user = request.user
            if user.is_authenticated and getattr(user, 'branch_id', None):
                qs = qs.filter(branch_id=user.branch_id)

        direction = request.query_params.get('direction')
        if direction in ('out', 'in'):
            qs = qs.filter(direction=direction)

        loans = list(qs.order_by('issued_date', 'id'))

        groups = defaultdict(lambda: {
            'counterparty': None,
            'branch_id': None,
            'direction': None,
            'loaned_total': 0,
            'paid_total': 0,
            'outstanding': 0,
            'open_loans': [],
        })

        for loan in loans:
            cp_id = loan.counterparty_id or f"manual:{loan.counterparty_name}|{loan.counterparty_phone}"
            key = (loan.branch_id, loan.direction, cp_id)
            paid = loan.paid_total()
            payload = loan.convert_json()

            entry = groups[key]
            entry['counterparty'] = loan.counterparty_payload()
            entry['branch_id'] = loan.branch_id
            entry['direction'] = loan.direction
            entry['loaned_total'] += payload['principal_amount']
            entry['paid_total'] += paid
            entry['outstanding'] += payload['remaining_amount']
            entry['open_loans'].append(payload)

        data = [g for g in groups.values() if g['outstanding'] > 0]

        return Response({'success': True, 'data': data})
