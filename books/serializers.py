from rest_framework import serializers
from django.utils.timezone import now
from .models import Book, BookImage, CollectedBookPayments, BalanceOverhead, BookOrder, CenterBalance, CenterOrders, \
    BranchPayment, EditorBalance, BookOverhead, UserBook
from branch.models import Branch
from payments.models import PaymentTypes
from branch.serializers import BranchSerializer
from payments.serializers import PaymentTypesSerializers
from user.serializers import UserSerializerRead, UserSalaryListSerializersRead
from students.serializers import StudentSerializer
from teachers.serializers import TeacherSerializer, TeacherSalaryListReadSerializers
from group.serializers import GroupSerializer
from user.models import CustomUser, UserSalary
from students.models import Student
from teachers.models import Teacher, TeacherSalary
from group.models import Group
from django.utils.timezone import now


class BookSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    old_id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255, required=False)
    desc = serializers.CharField(max_length=255, required=False)
    price = serializers.IntegerField(required=False)
    own_price = serializers.IntegerField(required=False)
    share_price = serializers.IntegerField(required=False)
    file = serializers.FileField(required=False)

    class Meta:
        model = Book
        fields = ['id', 'name', 'desc', 'price', 'own_price', 'share_price', 'file', 'old_id']


class BookImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    image = serializers.ImageField(required=False)
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = BookImage
        fields = ['id', 'image', 'book', 'old_id']


class BookImageListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    book = BookSerializer(required=False)
    image = serializers.ImageField(required=False)
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = BookImage
        fields = ['id', 'image', 'book', 'old_id']


class CollectedBookPaymentsSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    payment_type = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all())
    total_debt = serializers.IntegerField(required=False)
    month_date = serializers.DateField(required=False)
    received_date = serializers.DateField(required=False)
    status = serializers.BooleanField(required=False)
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = CollectedBookPayments
        fields = ['id', 'branch', 'payment_type', 'total_debt', 'month_date', 'received_date', 'status', 'old_id']

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


class CollectedBookPaymentsListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    branch = BranchSerializer(required=False)
    payment_type = PaymentTypesSerializers(required=False)
    total_debt = serializers.IntegerField(required=False)
    month_date = serializers.DateField(required=False)
    received_date = serializers.DateField(required=False)
    status = serializers.BooleanField(required=False)
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = CollectedBookPayments
        fields = ['id', 'branch', 'payment_type', 'total_debt', 'month_date', 'received_date', 'status', 'old_id']


class CenterBalanceListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    branch = BranchSerializer(required=False)
    total_money = serializers.IntegerField(required=False)
    remaining_money = serializers.IntegerField(required=False)
    taken_money = serializers.IntegerField(required=False)
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = CenterBalance
        fields = ['id', 'branch', 'total_money', 'remaining_money', 'taken_money', 'old_id']


class BalanceOverheadSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    balance = serializers.PrimaryKeyRelatedField(queryset=CenterBalance.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    payment_type = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all())
    overhead_sum = serializers.IntegerField(required=False)
    reason = serializers.CharField(required=False)
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = BalanceOverhead
        fields = ['id', 'branch', 'balance', 'payment_type', 'overhead_sum', 'reason', 'old_id']

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


class BalanceOverheadListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    balance = CenterBalanceListSerializer(required=False)
    branch = BranchSerializer(required=False)
    payment_type = PaymentTypesSerializers(required=False)
    overhead_sum = serializers.IntegerField(required=False)
    reason = serializers.CharField(required=False)
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = BalanceOverhead
        fields = ['id', 'branch', 'balance', 'payment_type', 'overhead_sum', 'reason', 'old_id']


class BookOrderSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    collected_payment = serializers.PrimaryKeyRelatedField(queryset=CollectedBookPayments.objects.all())
    count = serializers.IntegerField(required=False)
    admin_status = serializers.BooleanField(required=False)
    editor_status = serializers.BooleanField(required=False)
    reason = serializers.CharField(required=False)
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = BookOrder
        fields = ['id', 'user', 'book', 'student', 'teacher', 'group', 'branch', 'collected_payment', 'count',
                  'admin_status', 'editor_status', 'reason', 'old_id']

    def create(self, validated_data):
        book_order = BookOrder.objects.create(**validated_data)
        if not validated_data['student'] and not validated_data['teacher'] and not validated_data['group']:
            user = CustomUser.objects.get(pk=validated_data['user'])
            if user.teacher_user:
                user.teacher_user.teacher_id_salary.remaining_salary -= validated_data['payment_sum']
                user.teacher_user.teacher_id_salary.taken_salary += validated_data['payment_sum']
                UserBook.objects.create(
                    user=validated_data['user'],
                    branch=validated_data['branch'],
                    teacher_salary=user.teacher_user.teacher_id_salary,
                    book_order=book_order,
                    payment_sum=validated_data['payment_sum'],
                )

            else:
                user_salary = UserSalary.objects.get(user=user)
                user_salary.remaining_salary -= validated_data['payment_sum']
                user_salary.taken_salary += validated_data['payment_sum']
                UserBook.objects.create(
                    user=validated_data['user'],
                    branch=validated_data['branch'],
                    user_salary=user_salary,
                    book_order=book_order,
                    payment_sum=validated_data['payment_sum'],
                )
        return book_order

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if instance.admin_status == True:
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
        if instance.admin_status == True and instance.editor_status == True:
            branch = validated_data.pop('branch', None)
            payment_type = validated_data.pop('payment_type', None)
            count = instance.count
            price = instance.book.own_price
            payment_sum = count * price
            current_year = now().year
            current_month = now().month
            editor_balance = EditorBalance.objects.filter(date__year=current_year, date__month=current_month,
                                                          payment_type=payment_type)
            if editor_balance:
                editor_balance.balance += payment_sum
                editor_balance.payment_sum += payment_sum
                editor_balance.save()
            else:
                EditorBalance.objects.create(
                    payment_type=payment_type,
                    balance=payment_sum,
                    payment_sum=payment_sum,
                    overhead_sum=0
                )
            BranchPayment.objects.get_or_create(
                branch=branch,
                payment_type=payment_type,
                editor_balance=editor_balance,
                payment_sum=payment_sum,
                book_order=instance.id
            )
        return instance


class BookOrderListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    book = BookSerializer(required=False)
    user = UserSerializerRead(required=False)
    student = StudentSerializer(required=False)
    teacher = TeacherSerializer(required=False)
    group = GroupSerializer(required=False)
    branch = BranchSerializer(required=False)
    collected_payment = CollectedBookPaymentsSerializers(required=False)
    count = serializers.IntegerField(required=False)
    admin_status = serializers.BooleanField(required=False)
    editor_status = serializers.BooleanField(required=False)
    reason = serializers.CharField(required=False)
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = BookOrder
        fields = ['id', 'user', 'book', 'user', 'student', 'teacher', 'group', 'branch', 'collected_payment', 'count',
                  'admin_status', 'editor_status', 'reason', 'old_id']


class EditorBalanceListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    payment_type = PaymentTypesSerializers(required=False)
    balance = serializers.IntegerField(required=False)
    payment_sum = serializers.IntegerField(required=False)
    overhead_sum = serializers.IntegerField(required=False)
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = EditorBalance
        fields = ['id', 'payment_type', 'balance', 'payment_sum', 'overhead_sum', 'old_id']


class BranchPaymentListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    book_order = BookOrderListSerializers(required=False)
    editor_balance = EditorBalanceListSerializers(required=False)
    branch = BranchSerializer(required=False)
    payment_type = PaymentTypesSerializers(required=False)
    payment_sum = serializers.IntegerField(required=False)
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = BranchPayment
        fields = ['id', 'book_order', 'editor_balance', 'branch', 'payment_type', 'payment_sum', 'old_id']


class BookOverheadListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    editor_balance = EditorBalanceListSerializers(required=False)
    payment_type = PaymentTypesSerializers(required=False)
    price = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    deleted_reason = serializers.CharField(required=False)
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = BookOverhead
        fields = ['id', 'editor_balance', 'payment_type', 'price', 'name', 'deleted_reason', 'old_id']


class BookOverheadSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    editor_balance = serializers.PrimaryKeyRelatedField(queryset=EditorBalance.objects.all())
    payment_type = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all())
    price = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    deleted_reason = serializers.CharField(required=False)
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = BookOverhead
        fields = ['id', 'editor_balance', 'payment_type', 'price', 'name', 'deleted_reason', 'old_id']

    def create(self, validated_data):
        editor_balance = EditorBalance.objects.get(pk=validated_data.pop('editor_balance', None).pk)
        payment_type = PaymentTypes.objects.get(pk=validated_data.pop('payment_type', None).pk)
        price = validated_data.get('price')
        book_overhead = BookOverhead.objects.create(
            price=price,
            name=validated_data.get('name'),
            payment_type=payment_type,
            editor_balance=editor_balance

        )
        editor_balance.overhead_sum += price
        editor_balance.balance -= price
        editor_balance.save()
        return book_overhead


class UserBookSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    book_order = serializers.PrimaryKeyRelatedField(queryset=BookOrder.objects.all())
    teacher_salary = serializers.PrimaryKeyRelatedField(queryset=TeacherSalary.objects.all())
    user_salary = serializers.PrimaryKeyRelatedField(queryset=UserSalary.objects.all())

    def delete(self, instance):
        return instance

    class Meta:
        model = UserBook
        fields = '__all__'


class UserBookListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    user = UserSerializerRead(required=False)
    branch = BranchSerializer(required=False)
    book_order = BookOrderListSerializers(required=False)
    teacher_salary = TeacherSalaryListReadSerializers(required=False)
    user_salary = UserSalaryListSerializersRead(required=False)

    class Meta:
        model = UserBook
        fields = '__all__'
