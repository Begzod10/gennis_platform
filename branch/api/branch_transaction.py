from datetime import datetime

from django.db.models import Sum, Q
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

from branch.filters import BranchTransactionFilter
from branch.models import Branch, BranchTransaction
from branch.serializers import (
    BranchTransactionCreateRequestSerializer,
    BranchTransactionCreateResponseSerializer,
    BranchTransactionDeletedListResponseSerializer,
    BranchTransactionDeleteResponseSerializer,
    BranchTransactionErrorResponseSerializer,
    BranchTransactionListResponseSerializer,
    BranchTransactionListSerializer,
    BranchTransactionPaginatedListResponseSerializer,
    BranchTransactionUpdateRequestSerializer,
    BranchTransactionUpdateResponseSerializer,
)
from payments.models import PaymentTypes
from permissions.response import CustomPagination, QueryParamFilterMixin
from user.models import CustomUser


_ITEM_EXAMPLE = {
    "id": 17,
    "amount": 1500000,
    "is_give": True,
    "direction": "give",
    "reason": "Filial uchun avans",
    "person": {"id": 42, "name": "Ali", "surname": "Valiyev", "phone": "+998901112233"},
    "payment_type": {"id": 1, "name": "Cash"},
    "branch_id": 3,
    "date": "2026-04-30",
}

_ITEM_EXAMPLE_RECEIVE = {
    "id": 18,
    "amount": 800000,
    "is_give": False,
    "direction": "receive",
    "reason": "Filialdan qaytarildi",
    "person": {"id": None, "name": "Aziz", "surname": "Karimov", "phone": "+998935554433"},
    "payment_type": {"id": 2, "name": "Click"},
    "branch_id": 3,
    "date": "2026-04-29",
}


def _parse_date(s):
    try:
        return datetime.strptime(s, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


def _serialize_summary(qs):
    given = qs.filter(is_give=True).aggregate(s=Sum('amount'))['s'] or 0
    received = qs.filter(is_give=False).aggregate(s=Sum('amount'))['s'] or 0
    return {
        'total_given': given,
        'total_received': received,
        'net': received - given,
    }


@extend_schema(
    tags=['Branch Transactions'],
    summary='Filial tranzaksiyasini yaratish',
    description=(
        "Filial bo'yicha pul kirim/chiqimini yaratadi. "
        "`person_id` (tizim foydalanuvchisi) va `person_name` (qo'lda kiritish) "
        "ikkalasidan bittasi yuborilishi shart, ikkalasini birga yuborish mumkin emas."
    ),
    request=BranchTransactionCreateRequestSerializer,
    responses={
        201: BranchTransactionCreateResponseSerializer,
        400: BranchTransactionErrorResponseSerializer,
        404: BranchTransactionErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Tizim foydalanuvchisiga berildi',
            value={
                "amount": 1500000,
                "is_give": True,
                "reason": "Filial uchun avans",
                "payment_type_id": 1,
                "branch_id": 3,
                "date": "2026-04-30",
                "person_id": 42,
            },
            request_only=True,
        ),
        OpenApiExample(
            'Tashqi shaxsdan qabul qilindi',
            value={
                "amount": 800000,
                "is_give": False,
                "reason": "Filialdan qaytarildi",
                "payment_type_id": 2,
                "branch_id": 3,
                "date": "2026-04-29",
                "person_name": "Aziz",
                "person_surname": "Karimov",
                "person_phone": "+998935554433",
            },
            request_only=True,
        ),
        OpenApiExample(
            'Muvaffaqiyatli javob',
            value={
                "success": True,
                "message": "Tranzaksiya qo'shildi",
                "data": _ITEM_EXAMPLE,
            },
            response_only=True,
            status_codes=['201'],
        ),
        OpenApiExample(
            'Xatolik — majburiy maydon yo\'q',
            value={
                "success": False,
                "message": "amount, is_give, payment_type_id, branch_id, date kerak",
            },
            response_only=True,
            status_codes=['400'],
        ),
    ],
)
class BranchTransactionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        amount = data.get('amount')
        is_give = data.get('is_give')
        reason = data.get('reason')
        payment_type_id = data.get('payment_type_id')
        branch_id = data.get('branch_id')
        date_str = data.get('date')

        person_id = data.get('person_id')
        person_name = data.get('person_name')
        person_surname = data.get('person_surname')
        person_phone = data.get('person_phone')

        if amount is None or is_give is None or not payment_type_id or not branch_id or not date_str:
            return Response(
                {'success': False, 'message': 'amount, is_give, payment_type_id, branch_id, date kerak'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not person_id and not person_name:
            return Response(
                {'success': False, 'message': 'person_id yoki person_name kerak'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if person_id and person_name:
            return Response(
                {'success': False, 'message': 'person_id va person_name ikkalasini birga yuborish mumkin emas'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        date = _parse_date(date_str)
        if not date:
            return Response(
                {'success': False, 'message': 'date noto\'g\'ri formatda (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not Branch.objects.filter(id=branch_id).exists():
            return Response(
                {'success': False, 'message': 'Filial topilmadi'},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not PaymentTypes.objects.filter(id=payment_type_id).exists():
            return Response(
                {'success': False, 'message': "To'lov turi topilmadi"},
                status=status.HTTP_404_NOT_FOUND,
            )

        person = None
        if person_id:
            person = CustomUser.objects.filter(id=person_id).first()
            if not person:
                return Response(
                    {'success': False, 'message': 'Foydalanuvchi topilmadi'},
                    status=status.HTTP_404_NOT_FOUND,
                )

        tx = BranchTransaction.objects.create(
            amount=amount,
            is_give=bool(is_give),
            reason=reason,
            payment_type_id=payment_type_id,
            branch_id=branch_id,
            date=date,
            person=person,
            person_name=person_name if not person_id else None,
            person_surname=person_surname if not person_id else None,
            person_phone=person_phone if not person_id else None,
            created_by=request.user if request.user.is_authenticated else None,
        )

        return Response(
            {'success': True, 'message': "Tranzaksiya qo'shildi", 'data': tx.convert_json()},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=['Branch Transactions'],
    summary='Oylik tranzaksiyalar ro\'yxati',
    description=(
        "Berilgan oy/yil bo'yicha o'chirilmagan tranzaksiyalar ro'yxati va umumiy summa. "
        "`summary` har doim yo'nalish bo'yicha filtrsiz hisoblanadi (Flask bilan mos)."
    ),
    parameters=[
        OpenApiParameter('direction', OpenApiTypes.STR, OpenApiParameter.QUERY,
                         required=False, enum=['give', 'receive', 'all'],
                         description="Yo'nalish bo'yicha filtr; default 'all'"),
        OpenApiParameter('branch_id', OpenApiTypes.INT, OpenApiParameter.QUERY,
                         required=False, description='Filial ID bo\'yicha filtr'),
    ],
    responses={
        200: BranchTransactionListResponseSerializer,
        400: BranchTransactionErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Muvaffaqiyatli javob',
            value={
                "success": True,
                "summary": {
                    "total_given": 1500000,
                    "total_received": 800000,
                    "net": -700000,
                },
                "data": [_ITEM_EXAMPLE, _ITEM_EXAMPLE_RECEIVE],
            },
            response_only=True,
            status_codes=['200'],
        ),
    ],
)
class BranchTransactionMonthListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, month, year):
        direction = request.query_params.get('direction', 'all')
        branch_id = request.query_params.get('branch_id')

        qs = BranchTransaction.objects.filter(
            date__year=year,
            date__month=month,
            deleted=False,
        )
        if branch_id:
            try:
                qs = qs.filter(branch_id=int(branch_id))
            except (TypeError, ValueError):
                return Response(
                    {'success': False, 'message': 'branch_id noto\'g\'ri'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if direction == 'give':
            qs = qs.filter(is_give=True)
        elif direction == 'receive':
            qs = qs.filter(is_give=False)

        # Summary always reflects non-direction-filtered totals (matches Flask behaviour)
        summary_qs = BranchTransaction.objects.filter(
            date__year=year,
            date__month=month,
            deleted=False,
        )
        if branch_id:
            summary_qs = summary_qs.filter(branch_id=int(branch_id))

        return Response({
            'success': True,
            'summary': _serialize_summary(summary_qs),
            'data': [tx.convert_json() for tx in qs.order_by('-id')],
        })


@extend_schema(
    tags=['Branch Transactions'],
    summary='Tranzaksiyani yangilash',
    description=(
        "Tranzaksiyaning hech bo'lmaganda bitta maydonini yangilash. "
        "`person_id` yuborilsa qo'lda kiritilgan ism/familiya/telefon tozalanadi va aksincha. "
        "`branch_id` va `date` o'zgartirilmaydi (Flask bilan mos)."
    ),
    request=BranchTransactionUpdateRequestSerializer,
    responses={
        200: BranchTransactionUpdateResponseSerializer,
        404: BranchTransactionErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Summa va sababni yangilash',
            value={"amount": 1700000, "reason": "Avans qisman qaytarildi"},
            request_only=True,
        ),
        OpenApiExample(
            'Qo\'lda kiritishdan tizim foydalanuvchisiga o\'tkazish',
            value={"person_id": 42},
            request_only=True,
        ),
        OpenApiExample(
            'Muvaffaqiyatli javob',
            value={
                "success": True,
                "message": "Tranzaksiya yangilandi",
                "data": {**_ITEM_EXAMPLE, "amount": 1700000, "reason": "Avans qisman qaytarildi"},
            },
            response_only=True,
            status_codes=['200'],
        ),
    ],
)
class BranchTransactionUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        tx = BranchTransaction.objects.filter(id=pk, deleted=False).first()
        if not tx:
            return Response(
                {'success': False, 'message': 'Tranzaksiya topilmadi'},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = request.data

        if 'amount' in data:
            tx.amount = data['amount']
        if 'is_give' in data:
            tx.is_give = bool(data['is_give'])
        if 'reason' in data:
            tx.reason = data['reason']
        if 'payment_type_id' in data:
            if not PaymentTypes.objects.filter(id=data['payment_type_id']).exists():
                return Response(
                    {'success': False, 'message': "To'lov turi topilmadi"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            tx.payment_type_id = data['payment_type_id']

        if 'person_id' in data and data['person_id']:
            person = CustomUser.objects.filter(id=data['person_id']).first()
            if not person:
                return Response(
                    {'success': False, 'message': 'Foydalanuvchi topilmadi'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            tx.person = person
            tx.person_name = None
            tx.person_surname = None
            tx.person_phone = None
        elif 'person_name' in data:
            tx.person = None
            tx.person_name = data.get('person_name')
            tx.person_surname = data.get('person_surname')
            tx.person_phone = data.get('person_phone')

        tx.save()
        return Response({
            'success': True,
            'message': 'Tranzaksiya yangilandi',
            'data': tx.convert_json(),
        })


@extend_schema(
    tags=['Branch Transactions'],
    summary='Tranzaksiyani o\'chirish (soft-delete)',
    description="`deleted=True` qilib belgilaydi; jismoniy o'chirilmaydi.",
    responses={
        200: BranchTransactionDeleteResponseSerializer,
        404: BranchTransactionErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Muvaffaqiyatli javob',
            value={"success": True, "message": "Tranzaksiya o'chirildi"},
            response_only=True,
            status_codes=['200'],
        ),
        OpenApiExample(
            'Topilmadi',
            value={"success": False, "message": "Tranzaksiya topilmadi"},
            response_only=True,
            status_codes=['404'],
        ),
    ],
)
class BranchTransactionDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        tx = BranchTransaction.objects.filter(id=pk, deleted=False).first()
        if not tx:
            return Response(
                {'success': False, 'message': 'Tranzaksiya topilmadi'},
                status=status.HTTP_404_NOT_FOUND,
            )
        tx.deleted = True
        tx.save(update_fields=['deleted'])
        return Response({'success': True, 'message': "Tranzaksiya o'chirildi"})


@extend_schema(
    tags=['Branch Transactions'],
    summary='O\'chirilgan tranzaksiyalar ro\'yxati',
    description="Berilgan oy/yil bo'yicha soft-delete qilingan tranzaksiyalar (filtrlar bilan).",
    parameters=[
        OpenApiParameter('branch_id', OpenApiTypes.INT, OpenApiParameter.QUERY,
                         required=False, description='Filial ID'),
        OpenApiParameter('payment_type', OpenApiTypes.STR, OpenApiParameter.QUERY,
                         required=False, description="To'lov turi nomi"),
        OpenApiParameter('payment_type_id', OpenApiTypes.INT, OpenApiParameter.QUERY,
                         required=False, description="To'lov turi ID"),
        OpenApiParameter('is_give', OpenApiTypes.BOOL, OpenApiParameter.QUERY, required=False),
        OpenApiParameter('direction', OpenApiTypes.STR, OpenApiParameter.QUERY,
                         required=False, enum=['give', 'receive']),
        OpenApiParameter('amount_min', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
        OpenApiParameter('amount_max', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
        OpenApiParameter('loan_id', OpenApiTypes.STR, OpenApiParameter.QUERY, required=False,
                         description="Loan ID. 'null' qaytsa, qarzga ulanmagan tranzaksiyalar."),
        OpenApiParameter('search', OpenApiTypes.STR, OpenApiParameter.QUERY, required=False,
                         description="Sabab/ism/familiya bo'yicha qidiruv"),
        OpenApiParameter('limit', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
        OpenApiParameter('offset', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
    ],
    responses={
        200: BranchTransactionDeletedListResponseSerializer,
        400: BranchTransactionErrorResponseSerializer,
    },
    examples=[
        OpenApiExample(
            'Muvaffaqiyatli javob',
            value={
                "success": True,
                "total": 1,
                "data": [_ITEM_EXAMPLE],
            },
            response_only=True,
            status_codes=['200'],
        ),
    ],
)
class BranchTransactionDeletedListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, month, year):
        qp = request.query_params
        branch_id = qp.get('branch_id')
        payment_type_name = qp.get('payment_type')
        payment_type_id = qp.get('payment_type_id')
        is_give_param = qp.get('is_give')
        direction = (qp.get('direction') or '').strip().lower()
        amount_min = qp.get('amount_min')
        amount_max = qp.get('amount_max')
        loan_id_raw = qp.get('loan_id')
        search = (qp.get('search') or '').strip()
        limit = qp.get('limit')
        offset = qp.get('offset')

        qs = BranchTransaction.objects.filter(
            date__year=year,
            date__month=month,
            deleted=True,
        )

        if branch_id:
            try:
                qs = qs.filter(branch_id=int(branch_id))
            except (TypeError, ValueError):
                return Response(
                    {'success': False, 'message': 'branch_id noto\'g\'ri'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if payment_type_id:
            try:
                qs = qs.filter(payment_type_id=int(payment_type_id))
            except (TypeError, ValueError):
                return Response(
                    {'success': False, 'message': 'payment_type_id noto\'g\'ri'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif payment_type_name:
            pt = PaymentTypes.objects.filter(name=payment_type_name).first()
            if pt:
                qs = qs.filter(payment_type_id=pt.id)
            else:
                qs = qs.none()

        is_give_val = None
        if is_give_param is not None:
            v = str(is_give_param).strip().lower()
            if v in ('true', '1', 'yes'):
                is_give_val = True
            elif v in ('false', '0', 'no'):
                is_give_val = False
        if direction == 'give':
            is_give_val = True
        elif direction == 'receive':
            is_give_val = False
        if is_give_val is not None:
            qs = qs.filter(is_give=is_give_val)

        if amount_min is not None:
            try:
                qs = qs.filter(amount__gte=int(amount_min))
            except (TypeError, ValueError):
                pass
        if amount_max is not None:
            try:
                qs = qs.filter(amount__lte=int(amount_max))
            except (TypeError, ValueError):
                pass

        if loan_id_raw is not None:
            if str(loan_id_raw).strip().lower() == 'null':
                qs = qs.filter(loan__isnull=True)
            else:
                try:
                    qs = qs.filter(loan_id=int(loan_id_raw))
                except (TypeError, ValueError):
                    pass

        if search:
            qs = qs.filter(
                Q(reason__icontains=search)
                | Q(person_name__icontains=search)
                | Q(person_surname__icontains=search)
                | Q(person__name__icontains=search)
                | Q(person__surname__icontains=search)
            )

        total = qs.count()
        qs = qs.order_by('-id')

        try:
            offset_val = int(offset) if offset is not None else 0
        except (TypeError, ValueError):
            offset_val = 0
        try:
            limit_val = int(limit) if limit is not None else None
        except (TypeError, ValueError):
            limit_val = None

        if offset_val:
            qs = qs[offset_val:]
        if limit_val is not None:
            qs = qs[:limit_val]

        return Response({
            'success': True,
            'total': total,
            'data': [tx.convert_json() for tx in qs],
        })


@extend_schema(
    tags=['Branch Transactions'],
    summary='Tranzaksiyalar ro\'yxati (paginated)',
    description=(
        "Filtrlar va sahifalash bilan tranzaksiyalar ro'yxati. "
        "`?branch=` yuborilmasa, foydalanuvchining o'zining filiali ishlatiladi."
    ),
    parameters=[
        OpenApiParameter('branch', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False,
                         description='Filial ID. Berilmasa avtomatik foydalanuvchi filiali.'),
        OpenApiParameter('limit', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
        OpenApiParameter('offset', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
        OpenApiParameter('search', OpenApiTypes.STR, OpenApiParameter.QUERY, required=False,
                         description="Sabab/ism/familiya bo'yicha qidiruv"),
        OpenApiParameter('is_give', OpenApiTypes.BOOL, OpenApiParameter.QUERY, required=False),
        OpenApiParameter('direction', OpenApiTypes.STR, OpenApiParameter.QUERY, required=False,
                         enum=['give', 'receive']),
        OpenApiParameter('payment_type', OpenApiTypes.STR, OpenApiParameter.QUERY, required=False,
                         description="To'lov turi nomi bo'yicha (vergul bilan ajratilgan)"),
        OpenApiParameter('date_after', OpenApiTypes.DATE, OpenApiParameter.QUERY, required=False),
        OpenApiParameter('date_before', OpenApiTypes.DATE, OpenApiParameter.QUERY, required=False),
        OpenApiParameter('amount_min', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
        OpenApiParameter('amount_max', OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
    ],
    responses={200: BranchTransactionPaginatedListResponseSerializer},
    examples=[
        OpenApiExample(
            'Muvaffaqiyatli javob (paginated)',
            value={
                "count": 2,
                "next": None,
                "previous": None,
                "results": {
                    "data": [
                        {
                            "id": 17,
                            "amount": 1500000,
                            "is_give": True,
                            "direction": "give",
                            "reason": "Filial uchun avans",
                            "person": {"id": 42, "name": "Ali", "surname": "Valiyev", "phone": "+998901112233"},
                            "payment_type": {"id": 1, "name": "Cash"},
                            "branch_id": 9,
                            "date": "2026-04-30",
                        },
                    ],
                    "totalCount": [
                        {"name": "Total Amount", "totalPayment": 2300000, "totalPaymentCount": 2, "type": "amount"},
                        {"name": "Total Given", "totalPayment": 1500000, "totalPaymentCount": 1, "type": "given"},
                        {"name": "Total Received", "totalPayment": 800000, "totalPaymentCount": 1, "type": "received"},
                        {"name": "Net (received - given)", "totalPayment": -700000, "totalPaymentCount": 2, "type": "net"},
                        {"name": "Cash Payments", "totalPayment": 1500000, "totalPaymentCount": 1, "type": "cash"},
                        {"name": "Click Payments", "totalPayment": 800000, "totalPaymentCount": 1, "type": "click"},
                        {"name": "Bank Transfers", "totalPayment": 0, "totalPaymentCount": 0, "type": "bank"},
                    ],
                },
            },
            response_only=True,
            status_codes=['200'],
        ),
    ],
)
class BranchTransactionListView(QueryParamFilterMixin, generics.ListAPIView):
    filter_mappings = {
        'branch': 'branch_id',
    }
    permission_classes = [IsAuthenticated]
    search_fields = ['reason', 'person__name', 'person__surname', 'person_name', 'person_surname']

    queryset = BranchTransaction.objects.filter(deleted=False).select_related(
        'payment_type', 'person', 'branch',
    )
    serializer_class = BranchTransactionListSerializer
    filterset_class = BranchTransactionFilter
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]

    def list(self, request, *args, **kwargs):
        # Reset filter_conditions per request — QueryParamFilterMixin uses class attr
        self.filter_conditions = Q()
        queryset = self.filter_queryset(self.get_queryset()).order_by('-date', '-id')

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        given_qs = queryset.filter(is_give=True)
        received_qs = queryset.filter(is_give=False)
        total_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0
        given_total = given_qs.aggregate(total=Sum('amount'))['total'] or 0
        received_total = received_qs.aggregate(total=Sum('amount'))['total'] or 0

        cash_qs = queryset.filter(payment_type__name__iexact='Cash')
        click_qs = queryset.filter(payment_type__name__iexact='Click')
        bank_qs = queryset.filter(payment_type__name__iexact='Bank')

        total_count = [
            {
                "name": "Total Amount",
                "totalPayment": total_amount,
                "totalPaymentCount": queryset.count(),
                "type": "amount",
            },
            {
                "name": "Total Given",
                "totalPayment": given_total,
                "totalPaymentCount": given_qs.count(),
                "type": "given",
            },
            {
                "name": "Total Received",
                "totalPayment": received_total,
                "totalPaymentCount": received_qs.count(),
                "type": "received",
            },
            {
                "name": "Net (received - given)",
                "totalPayment": received_total - given_total,
                "totalPaymentCount": queryset.count(),
                "type": "net",
            },
            {
                "name": "Cash Payments",
                "totalPayment": cash_qs.aggregate(total=Sum('amount'))['total'] or 0,
                "totalPaymentCount": cash_qs.count(),
                "type": "cash",
            },
            {
                "name": "Click Payments",
                "totalPayment": click_qs.aggregate(total=Sum('amount'))['total'] or 0,
                "totalPaymentCount": click_qs.count(),
                "type": "click",
            },
            {
                "name": "Bank Transfers",
                "totalPayment": bank_qs.aggregate(total=Sum('amount'))['total'] or 0,
                "totalPaymentCount": bank_qs.count(),
                "type": "bank",
            },
        ]

        return self.get_paginated_response({
            'data': serializer.data,
            'totalCount': total_count,
        })
