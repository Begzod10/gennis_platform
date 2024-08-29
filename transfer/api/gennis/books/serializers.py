from rest_framework import serializers

from books.models import CollectedBookPayments, BookOrder, Book, CenterBalance, BalanceOverhead, EditorBalance, \
    BranchPayment, UserBook
from branch.models import Branch
from group.models import Group
from payments.models import PaymentTypes
from students.models import Student
from teachers.models import Teacher, TeacherSalary
from user.models import CustomUser, UserSalary


class OldIdRelatedField(serializers.SlugRelatedField):
    def __init__(self, *args, **kwargs):
        kwargs['slug_field'] = 'old_id'
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        model = self.queryset.model
        try:
            return model.objects.get(old_id=data)
        except model.DoesNotExist:
            raise serializers.ValidationError(f"{model.__name__} with old_id {data} does not exist.")


class TransferUserBookSerializer(serializers.ModelSerializer):
    user = OldIdRelatedField(queryset=CustomUser.objects.all(), required=False,
                             allow_null=True)
    book_order = OldIdRelatedField(queryset=BookOrder.objects.all(), required=False,
                                   allow_null=True)
    branch = OldIdRelatedField(queryset=Branch.objects.all(), required=False,
                               allow_null=True)
    teacher_salary = OldIdRelatedField(queryset=TeacherSalary.objects.all(),
                                       required=False,
                                       allow_null=True)
    user_salary = OldIdRelatedField(queryset=UserSalary.objects.all(), required=False,
                                    allow_null=True)

    class Meta:
        model = UserBook
        fields = '__all__'


class TransferBranchPaymentSerializer(serializers.ModelSerializer):
    book_order = OldIdRelatedField(queryset=BookOrder.objects.all())
    editor_balance = OldIdRelatedField(queryset=EditorBalance.objects.all())
    branch = OldIdRelatedField(queryset=Branch.objects.all())
    payment_type = OldIdRelatedField(queryset=PaymentTypes.objects.all())

    class Meta:
        model = BranchPayment
        fields = '__all__'


class TransferEditorBalanceSerializer(serializers.ModelSerializer):
    payment_type = OldIdRelatedField(queryset=PaymentTypes.objects.all())

    class Meta:
        model = EditorBalance
        fields = '__all__'


class TransferBalanceOverheadSerializer(serializers.ModelSerializer):
    balance = OldIdRelatedField(queryset=CenterBalance.objects.all())
    branch = OldIdRelatedField(queryset=Branch.objects.all())
    payment_type = OldIdRelatedField(queryset=PaymentTypes.objects.all())

    class Meta:
        model = BalanceOverhead
        fields = '__all__'


class TransferCenterBalanceSerializer(serializers.ModelSerializer):
    branch = OldIdRelatedField(queryset=Branch.objects.all())

    class Meta:
        model = CenterBalance
        fields = '__all__'


class TransferCollectedBookPaymentsSerializer(serializers.ModelSerializer):
    branch = OldIdRelatedField(queryset=Branch.objects.all())
    payment_type = OldIdRelatedField(queryset=PaymentTypes.objects.all())

    class Meta:
        model = CollectedBookPayments
        fields = '__all__'


class TransferBookOrderSerializer(serializers.ModelSerializer):
    user = OldIdRelatedField(queryset=CustomUser.objects.all(), required=False,
                             allow_null=True)
    student = OldIdRelatedField(queryset=Student.objects.all(), required=False,
                                allow_null=True)
    teacher = OldIdRelatedField(queryset=Teacher.objects.all(), required=False,
                                allow_null=True)
    group = OldIdRelatedField(queryset=Group.objects.all(), required=False,
                              allow_null=True)
    book = OldIdRelatedField(queryset=Book.objects.all(), required=False,
                             allow_null=True)
    branch = OldIdRelatedField(queryset=Branch.objects.all(), required=False,
                               allow_null=True)
    collected_payment = OldIdRelatedField(queryset=CollectedBookPayments.objects.all(),
                                          required=False, allow_null=True)

    class Meta:
        model = BookOrder
        fields = '__all__'
