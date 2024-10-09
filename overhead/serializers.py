from datetime import datetime

from rest_framework import serializers

from branch.models import Branch
from branch.serializers import BranchSerializer
from payments.serializers import PaymentTypes, PaymentTypesSerializers
from .models import Overhead, OverheadType


class OverheadSerializerCreate(serializers.ModelSerializer):
    price = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    payment = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    type = serializers.PrimaryKeyRelatedField(queryset=OverheadType.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Overhead
        fields = ['id', 'name', 'payment', 'price', 'branch', 'type']

    def create(self, validated_data):
        month = validated_data.get('month')
        day = validated_data.get('day')
        current_year = datetime.now().year
        date = datetime(year=current_year, month=month, day=day)
        overhead = Overhead.objects.create(**validated_data, created=date)
        return overhead


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


class MonthDaysSerializer(serializers.Serializer):
    days = serializers.ListField(child=serializers.IntegerField())
    name = serializers.CharField(max_length=3)
    value = serializers.CharField(max_length=2)
