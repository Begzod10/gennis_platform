from rest_framework import serializers

from books.models import CollectedBookPayments, BookOrder, Book, CenterBalance, BalanceOverhead, EditorBalance, \
    BranchPayment, UserBook
from branch.models import Branch
from group.models import Group
from payments.models import PaymentTypes
from students.models import Student
from teachers.models import Teacher, TeacherSalary
from user.models import CustomUser, UserSalary


class TransferUserBookSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(queryset=CustomUser.objects.all(), slug_field='old_id', required=False,
                                        allow_null=True)
    book_order = serializers.SlugRelatedField(queryset=BookOrder.objects.all(), slug_field='old_id', required=False,
                                              allow_null=True)
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id', required=False,
                                          allow_null=True)
    teacher_salary = serializers.SlugRelatedField(queryset=TeacherSalary.objects.all(), slug_field='old_id',
                                                  required=False,
                                                  allow_null=True)
    user_salary = serializers.SlugRelatedField(queryset=UserSalary.objects.all(), slug_field='old_id', required=False,
                                               allow_null=True)

    class Meta:
        model = UserBook
        fields = '__all__'


class TransferBranchPaymentSerializer(serializers.ModelSerializer):
    book_order = serializers.SlugRelatedField(queryset=BookOrder.objects.all(), slug_field='old_id')
    editor_balance = serializers.SlugRelatedField(queryset=EditorBalance.objects.all(), slug_field='old_id')
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id')
    payment_type = serializers.SlugRelatedField(queryset=PaymentTypes.objects.all(), slug_field='old_id')

    class Meta:
        model = BranchPayment
        fields = '__all__'


class TransferEditorBalanceSerializer(serializers.ModelSerializer):
    payment_type = serializers.SlugRelatedField(queryset=PaymentTypes.objects.all(), slug_field='old_id')

    class Meta:
        model = EditorBalance
        fields = '__all__'


class TransferBalanceOverheadSerializer(serializers.ModelSerializer):
    balance = serializers.SlugRelatedField(queryset=CenterBalance.objects.all(), slug_field='old_id')
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id')
    payment_type = serializers.SlugRelatedField(queryset=PaymentTypes.objects.all(), slug_field='old_id')

    class Meta:
        model = BalanceOverhead
        fields = '__all__'


class TransferCenterBalanceSerializer(serializers.ModelSerializer):
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id')

    class Meta:
        model = CenterBalance
        fields = '__all__'


class TransferCollectedBookPaymentsSerializer(serializers.ModelSerializer):
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id')
    payment_type = serializers.SlugRelatedField(queryset=PaymentTypes.objects.all(), slug_field='old_id')

    class Meta:
        model = CollectedBookPayments
        fields = '__all__'


class TransferBookOrderSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(queryset=CustomUser.objects.all(), slug_field='old_id', required=False,
                                        allow_null=True)
    student = serializers.SlugRelatedField(queryset=Student.objects.all(), slug_field='old_id', required=False,
                                           allow_null=True)
    teacher = serializers.SlugRelatedField(queryset=Teacher.objects.all(), slug_field='old_id', required=False,
                                           allow_null=True)
    group = serializers.SlugRelatedField(queryset=Group.objects.all(), slug_field='old_id', required=False,
                                         allow_null=True)
    book = serializers.SlugRelatedField(queryset=Book.objects.all(), slug_field='old_id', required=False,
                                        allow_null=True)
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id', required=False,
                                          allow_null=True)
    collected_payment = serializers.SlugRelatedField(queryset=CollectedBookPayments.objects.all(), slug_field='old_id',
                                                     required=False, allow_null=True)

    class Meta:
        model = BookOrder
        fields = '__all__'
