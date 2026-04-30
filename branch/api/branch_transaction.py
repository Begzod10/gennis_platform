from datetime import datetime

from django.db.models import Sum, Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from branch.models import Branch, BranchTransaction
from payments.models import PaymentTypes
from user.models import CustomUser


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


class BranchTransactionCreateView(APIView):
    """
    POST /branch_transaction/
    Body: amount, is_give, reason?, payment_type_id, branch_id, date (YYYY-MM-DD),
          person_id  XOR  person_name/person_surname/person_phone
    """
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


class BranchTransactionMonthListView(APIView):
    """
    GET /branch_transaction/<month>/<year>/
    Query params:
        direction: give | receive | all (default all)
        branch_id: int (optional)
    """
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


class BranchTransactionUpdateView(APIView):
    """PUT /branch_transaction/<int:pk>/"""
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


class BranchTransactionDeleteView(APIView):
    """DELETE /branch_transaction/<int:pk>/  (soft-delete)"""
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


class BranchTransactionDeletedListView(APIView):
    """
    GET /branch_transaction/deleted/<month>/<year>/
    Query params:
        branch_id: int (optional)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, month, year):
        branch_id = request.query_params.get('branch_id')

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

        return Response({
            'success': True,
            'data': [tx.convert_json() for tx in qs.order_by('-id')],
        })
