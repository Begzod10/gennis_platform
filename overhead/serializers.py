import pprint
from datetime import datetime

from rest_framework import serializers

from branch.models import Branch
from branch.serializers import BranchSerializer
from payments.serializers import PaymentTypes, PaymentTypesSerializers
from .models import Overhead, OverheadType, OverheadTypeLog


class OverheadSerializerCreate(serializers.ModelSerializer):
    price = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    payment = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    type = serializers.PrimaryKeyRelatedField(queryset=OverheadType.objects.all(), allow_null=True, required=False)



    class Meta:
        model = Overhead
        fields = ['id', 'name', 'payment', 'price', 'branch', 'type', 'created']

    def create(self, validated_data):
        overhead = Overhead.objects.create(**validated_data)
        return overhead

    def get_created(self, obj):
        return obj.created.strftime('%Y-%m-%d')

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if not representation.get('name') and instance.type:
            representation['name'] = instance.type.name

        if instance.payment:
            representation['payment'] = {
                'id': instance.payment.id,
                'name': instance.payment.name
            }

        return representation


class OverheadSerializerGet(serializers.ModelSerializer):
    payment = PaymentTypesSerializers(read_only=True)
    branch = BranchSerializer(read_only=True)
    created = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Overhead
        fields = '__all__'

    def get_created(self, obj):
        return obj.created.strftime('%Y-%m-%d')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if not ret['name'] and instance.type:
            ret['name'] = instance.type.name
        return ret


class OverheadSerializerGetTYpe(serializers.ModelSerializer):
    class Meta:
        model = OverheadType
        fields = '__all__'


class OverheadTypeLogSerializer(serializers.ModelSerializer):
    overhead_type_name = serializers.CharField(source='overhead_type.name', read_only=True)

    class Meta:
        model = OverheadTypeLog
        fields = '__all__'


class OverheadTypeListItemSerializer(serializers.Serializer):
    """One overhead type row returned by /overheads_type/."""
    id = serializers.IntegerField()
    name = serializers.CharField()
    cost = serializers.IntegerField(allow_null=True)
    changeable = serializers.BooleanField()
    order = serializers.IntegerField(allow_null=True)
    branch_id = serializers.IntegerField(allow_null=True)


class OverheadTypeListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    data = OverheadTypeListItemSerializer(many=True)


class OverheadTypeLogItemSerializer(serializers.Serializer):
    """One log row in the /overhead_type_logs/<month>/<year>/ response.data list."""
    id = serializers.IntegerField()
    overhead_type_id = serializers.IntegerField()
    overhead_type_name = serializers.CharField()
    cost = serializers.IntegerField(allow_null=True)
    is_paid = serializers.BooleanField()
    is_prepaid = serializers.BooleanField()
    paid_date = serializers.CharField(allow_null=True, help_text="dd.mm.YYYY")
    overhead_id = serializers.IntegerField(allow_null=True)
    branch_id = serializers.IntegerField(allow_null=True)
    date = serializers.CharField(allow_null=True, help_text="dd.mm.YYYY")


class OverheadTypeLogSummarySerializer(serializers.Serializer):
    total_count = serializers.IntegerField()
    paid_count = serializers.IntegerField()
    unpaid_count = serializers.IntegerField()
    total_sum = serializers.IntegerField()
    paid_sum = serializers.IntegerField()
    unpaid_sum = serializers.IntegerField()


class OverheadTypeLogListResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    summary = OverheadTypeLogSummarySerializer()
    data = OverheadTypeLogItemSerializer(many=True)


class OverheadTypeLogGenerateRequestSerializer(serializers.Serializer):
    branch_id = serializers.IntegerField(required=False, allow_null=True, help_text="Branch ID; omit for global logs")


class OverheadTypeLogGenerateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()


class OverheadTypeLogPayRequestSerializer(serializers.Serializer):
    payment_type_id = serializers.IntegerField(help_text="PaymentTypes.id")
    branch_id = serializers.IntegerField(required=False, allow_null=True, help_text="Branch.id")
    date = serializers.DateField(help_text="Payment date YYYY-MM-DD")
    log_id = serializers.IntegerField(required=False, allow_null=True,
                                      help_text="Same-month payment: id of the OverheadTypeLog being paid")
    overhead_type_id = serializers.IntegerField(required=False, allow_null=True,
                                                help_text="Prepayment: id of OverheadType")
    paid_for_month = serializers.CharField(required=False, allow_null=True,
                                           help_text="Prepayment: 'YYYY-MM' month being paid for")


class OverheadTypeLogPayResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    log = OverheadTypeLogItemSerializer(required=False)


class MonthDaysSerializer(serializers.Serializer):
    days = serializers.ListField(child=serializers.IntegerField())
    name = serializers.CharField(max_length=3)
    value = serializers.CharField(max_length=2)
