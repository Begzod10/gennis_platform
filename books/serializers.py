from rest_framework import serializers
from django.utils.timezone import now
from .models import Book, BookImage, CollectedBookPayments, BalanceOverhead, BookOrder, CenterBalance, CenterOrders
from branch.models import Branch
from payments.models import PaymentTypes
from branch.serializers import BranchSerializer
from payments.serializers import PaymentTypesSerializers
from user.serializers import UserSerializer
from students.serializers import StudentSerializer
from teachers.serializers import TeacherSerializer
from group.serializers import GroupSerializer


class BookSerializer(serializers.ModelSerializer):



    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255, required=False)
    desc = serializers.CharField(max_length=255, required=False)
    price = serializers.IntegerField(required=False)
    own_price = serializers.IntegerField(required=False)
    share_price = serializers.IntegerField(required=False)
    file = serializers.FileField(required=False)

    class Meta:
        model = Book
        fields = ['id', 'name', 'desc', 'price', 'own_price', 'share_price', 'file']


class BookImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    book = BookSerializer(required=False)
    image = serializers.ImageField(required=False)

    class Meta:
        model = BookImage
        fields = ['id', 'image', 'book']


class CollectedBookPaymentsSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    branch = BranchSerializer(required=False)
    payment_type = PaymentTypesSerializers(required=False)
    total_debt = serializers.IntegerField(required=False)
    month_date = serializers.DateTimeField(required=False)
    received_date = serializers.DateTimeField(required=False)
    status = serializers.BooleanField(required=False)

    class Meta:
        model = CollectedBookPayments
        fields = ['id', 'branch', 'payment_type', 'total_debt', 'month_date', 'received_date', 'status']

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


class CenterBalanceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    branch = BranchSerializer(required=False)
    total_money = serializers.IntegerField(required=False)
    remaining_money = serializers.IntegerField(required=False)
    taken_money = serializers.IntegerField(required=False)

    class Meta:
        model = CenterBalance
        fields = ['id', 'branch', 'total_money', 'remaining_money', 'taken_money']


class BalanceOverheadSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    balance = CenterBalanceSerializer(required=False)
    branch = BranchSerializer(required=False)
    payment_type = PaymentTypesSerializers(required=False)
    overhead_sum = serializers.IntegerField(required=False)
    reason = serializers.CharField(required=False)

    class Meta:
        model = BalanceOverhead
        fields = ['id', 'branch', 'balance', 'payment_type', 'overhead_sum', 'reason']

    def create(self, validated_data):
        branch = Branch.objects.get(pk=validated_data.pop('branch', None).pk)
        balance = CenterBalance.objects.get(pk=validated_data.pop('balance', None).pk)
        payment_type = PaymentTypes.objects.get(pk=validated_data.pop('payment_type', None).pk)
        overhead_sum = validated_data.get('overhead_sum')
        balance_overhead = BalanceOverhead.objects.create(
            overhead_sum=overhead_sum,
            reason=validated_data.get('reason'),
            payment_type=payment_type,
            branch=branch,
            balance=balance,
        )
        balance.remaining_money -= overhead_sum
        balance.taken_money += overhead_sum
        balance.save()
        return balance_overhead

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        instance.balance.taken_money -= instance.overhead_sum
        instance.balance.remaining_money += instance.overhead_sum
        instance.balance.save()
        return instance


class BookOrderSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    book = BookSerializer(required=False)
    user = UserSerializer(required=False)
    student = StudentSerializer(required=False)
    teacher = TeacherSerializer(required=False)
    group = GroupSerializer(required=False)
    branch = BranchSerializer(required=False)
    collected_payment = CollectedBookPaymentsSerializers(required=False)
    count = serializers.IntegerField(required=False)
    admin_status = serializers.BooleanField(required=False)
    editor_status = serializers.BooleanField(required=False)
    reason = serializers.CharField(required=False)

    class Meta:
        model = BookOrder
        fields = ['id', 'user', 'book', 'user', 'student', 'teacher', 'group', 'branch', 'collected_payment', 'count',
                  'admin_status', 'editor_status', 'reason']

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
