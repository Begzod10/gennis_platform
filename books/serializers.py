from rest_framework import serializers
from django.utils.timezone import now
from .models import Book, BookImage, CollectedBookPayments, BalanceOverhead, BookOrder, CenterBalance, CenterOrders
from branch.models import Branch
from payments.models import PaymentTypes


class BookOrderSerializers(serializers.ModelSerializer):
    class Meta:
        model = BookOrder
        fields = '__all__'

    def update(self, instance, validated_data):
        admin_status = validated_data.pop('admin_status', None)
        if admin_status and admin_status == True:
            branch = validated_data.pop('branch', None)
            payment_type = validated_data.pop('payment_type', None)
            count = instance.count
            price = instance.book.own_price
            total_debt = count * price
            collected_book_payments = CollectedBookPayments.objects.get(status=False)
            if not collected_book_payments:
                CollectedBookPayments.objects.create(branch=branch, payment_type=payment_type,
                                                     total_debt=total_debt,
                                                     month_date=validated_data.pop('month_date'))
            else:
                collected_book_payments.total_debt += total_debt
                collected_book_payments.save()
            instance.admin_status = True
            instance.save()
            return instance


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'name', 'desc', 'price', 'own_price', 'share_price', 'file']


class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookImage
        fields = ['id', 'image', 'book']


class CollectedBookPaymentsSerializers(serializers.ModelSerializer):
    class Meta:
        model = CollectedBookPayments
        fields = '__all__'

    def update(self, instance, validated_data):
        status = validated_data.pop('status', None)
        if status and status == True:
            branch = validated_data.pop('branch', None)
            book_orders = BookOrder.objects.get(collected_payment=instance.pk).all()
            total_money = 0
            current_year = now().year
            current_month = now().month
            center_balance = CenterBalance.objects.get(month_date__year=current_year, branch=branch,
                                                       month_date__month=current_month)
            for book_order in book_orders:
                count = book_order.count
                price = book_order.book.own_price
                total = count * price
                total_money += total
            if not center_balance:
                center_balance = CenterBalance.objects.create(
                    branch=branch,
                    total_money=total_money,
                    remaining_money=total_money,
                    taken_money=0,
                )
            else:
                center_balance.total_money += total_money
                center_balance.remaining_money += total_money
                center_balance.save()
            for book_order in book_orders:
                CenterOrders.objects.create(
                    order=book_order,
                    balance=center_balance
                )
            instance.status = True
            instance.save()
            return instance


class BalanceOverheadSerializers(serializers.ModelSerializer):
    class Meta:
        model = BalanceOverhead
        fields = '__all__'

    def create(self, validated_data):
        branch_data = validated_data.pop('branch', None)
        branch = Branch.objects.get(name=branch_data['name'])
        center_balance = CenterBalance.objects.get(pk=validated_data.pop('center_balance', None))
        payment_type = PaymentTypes.objects.get(pk=validated_data.pop('payment_type', None))
        overhead_sum = validated_data.get('overhead_sum')
        balance_overhead = BalanceOverhead.objects.create(
            overhead_sum=overhead_sum,
            reason=validated_data.get('reason'),
            payment_type=payment_type,
            branch=branch,
            balance=center_balance,
        )
        center_balance.remaining_money -= overhead_sum
        center_balance.taken_money += overhead_sum
        center_balance.save()
        return balance_overhead

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        instance.balance.taken_money -= instance.overhead_sum
        instance.balance.remaining_money += instance.overhead_sum
        instance.balance.save()
        return instance
