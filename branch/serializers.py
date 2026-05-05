from rest_framework import serializers

from location.serializers import LocationListSerializers, Location
from .models import Branch, BranchLoan, BranchTransaction


class BranchLoanCounterpartySerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True)
    name = serializers.CharField(allow_null=True)
    surname = serializers.CharField(allow_null=True)
    phone = serializers.CharField(allow_null=True)


class BranchLoanItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    branch_id = serializers.IntegerField()
    counterparty = BranchLoanCounterpartySerializer()
    direction = serializers.ChoiceField(choices=['out', 'in'])
    principal_amount = serializers.IntegerField()
    paid_total = serializers.IntegerField()
    remaining_amount = serializers.IntegerField()
    is_settled = serializers.BooleanField()
    issued_date = serializers.CharField(help_text="YYYY-MM-DD")
    due_date = serializers.CharField(allow_null=True, help_text="YYYY-MM-DD")
    settled_date = serializers.CharField(allow_null=True, help_text="YYYY-MM-DD")
    reason = serializers.CharField(allow_null=True)
    notes = serializers.CharField(allow_null=True)
    status = serializers.ChoiceField(choices=['active', 'settled', 'cancelled'])
    cancelled_reason = serializers.CharField(allow_null=True)
    management_id = serializers.IntegerField(allow_null=True)


class BranchLoanCreateRequestSerializer(serializers.Serializer):
    branch_id = serializers.IntegerField()
    direction = serializers.ChoiceField(choices=['out', 'in'])
    principal_amount = serializers.IntegerField()
    issued_date = serializers.DateField()
    due_date = serializers.DateField(required=False, allow_null=True)
    payment_type_id = serializers.IntegerField(help_text="PaymentTypes.id for the disbursement transaction")
    reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    counterparty_id = serializers.IntegerField(required=False, allow_null=True)
    counterparty_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    counterparty_surname = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    counterparty_phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class BranchLoanUpdateRequestSerializer(serializers.Serializer):
    due_date = serializers.DateField(required=False, allow_null=True)
    reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class BranchLoanRepayRequestSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    payment_type_id = serializers.IntegerField()
    date = serializers.DateField()
    reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class BranchLoanCancelRequestSerializer(serializers.Serializer):
    cancelled_reason = serializers.CharField()


class BranchLoanSimpleResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = BranchLoanItemSerializer()


class BranchLoanErrorResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    message = serializers.CharField()


class BranchLoanOutstandingItemSerializer(serializers.Serializer):
    counterparty = BranchLoanCounterpartySerializer()
    branch_id = serializers.IntegerField()
    direction = serializers.ChoiceField(choices=['out', 'in'])
    loaned_total = serializers.IntegerField()
    paid_total = serializers.IntegerField()
    outstanding = serializers.IntegerField()
    open_loans = BranchLoanItemSerializer(many=True)


class BranchLoanOutstandingResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    data = BranchLoanOutstandingItemSerializer(many=True)


class BranchLoanListSerializer(serializers.ModelSerializer):
    """Wraps BranchLoan.convert_json() for paginated list responses."""

    class Meta:
        model = BranchLoan
        fields = ['id']

    def to_representation(self, instance):
        return instance.convert_json()


class BranchLoanPaginatedListResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = serializers.DictField()


class BranchTransactionListSerializer(serializers.ModelSerializer):
    """Wraps BranchTransaction.convert_json() for paginated list responses."""

    class Meta:
        model = BranchTransaction
        fields = ['id']

    def to_representation(self, instance):
        return instance.convert_json()


class BranchTransactionTotalsRowSerializer(serializers.Serializer):
    name = serializers.CharField()
    totalPayment = serializers.IntegerField()
    totalPaymentCount = serializers.IntegerField()
    type = serializers.CharField()


class BranchTransactionPaginatedListResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = serializers.DictField()


class BranchSerializer(serializers.ModelSerializer):
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())

    class Meta:
        model = Branch
        fields = '__all__'


class BranchTransactionPersonSerializer(serializers.Serializer):
    id = serializers.IntegerField(allow_null=True)
    name = serializers.CharField(allow_null=True)
    surname = serializers.CharField(allow_null=True)
    phone = serializers.CharField(allow_null=True)


class BranchTransactionPaymentTypeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(allow_null=True)


class BranchTransactionItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()
    is_give = serializers.BooleanField()
    direction = serializers.ChoiceField(choices=['give', 'receive'])
    reason = serializers.CharField(allow_null=True)
    person = BranchTransactionPersonSerializer()
    payment_type = BranchTransactionPaymentTypeSerializer()
    branch_id = serializers.IntegerField()
    date = serializers.CharField(help_text="YYYY-MM-DD")


class BranchTransactionCreateRequestSerializer(serializers.Serializer):
    amount = serializers.IntegerField(help_text="Pul miqdori")
    is_give = serializers.BooleanField(help_text="True = berildi, False = qabul qilindi")
    payment_type_id = serializers.IntegerField(help_text="PaymentTypes.id")
    branch_id = serializers.IntegerField(help_text="Branch.id")
    date = serializers.DateField(help_text="YYYY-MM-DD")
    reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    person_id = serializers.IntegerField(
        required=False, allow_null=True,
        help_text="CustomUser.id — person_name bilan birga yuborilmasin",
    )
    person_name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True,
        help_text="Tizimda bo'lmagan shaxs uchun ism — person_id bilan birga yuborilmasin",
    )
    person_surname = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    person_phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class BranchTransactionUpdateRequestSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=False)
    is_give = serializers.BooleanField(required=False)
    reason = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    payment_type_id = serializers.IntegerField(required=False)
    person_id = serializers.IntegerField(required=False, allow_null=True)
    person_name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    person_surname = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    person_phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class BranchTransactionSummarySerializer(serializers.Serializer):
    total_given = serializers.IntegerField()
    total_received = serializers.IntegerField()
    net = serializers.IntegerField()


class BranchTransactionCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = BranchTransactionItemSerializer()


class BranchTransactionUpdateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = BranchTransactionItemSerializer()


class BranchTransactionListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    summary = BranchTransactionSummarySerializer()
    data = BranchTransactionItemSerializer(many=True)


class BranchTransactionDeletedListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    data = BranchTransactionItemSerializer(many=True)


class BranchTransactionDeleteResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()


class BranchTransactionErrorResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    message = serializers.CharField()


class BranchListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    location = LocationListSerializers(required=False)
    name = serializers.CharField(max_length=255, required=False)
    number = serializers.CharField(required=False)
    map_link = serializers.CharField(required=False)
    code = serializers.IntegerField(required=False)
    phone_number = serializers.CharField(max_length=20, required=False)
    director_fio = serializers.CharField(max_length=255, required=False)
    location_text = serializers.CharField(max_length=255, required=False)
    district = serializers.CharField(max_length=255, required=False)
    bank_sheet = serializers.CharField(required=False)
    inn = serializers.CharField(max_length=255, required=False)
    bank = serializers.CharField(max_length=255, required=False)
    mfo = serializers.CharField(max_length=50, required=False)
    campus_name = serializers.CharField(max_length=255, required=False)
    address = serializers.CharField(max_length=255, required=False)
    year = serializers.DateField(required=False)
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = Branch
        fields = ['id', 'name', 'number', 'location', 'map_link', 'code', 'phone_number',
                  'director_fio', 'location_text', 'district', 'bank_sheet', 'inn',
                  'bank', 'mfo', 'campus_name', 'address', 'year', 'old_id']
