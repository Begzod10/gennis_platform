from rest_framework import serializers

from branch.models import Branch
from branch.serializers import BranchSerializer
from payments.serializers import PaymentTypes, PaymentTypesSerializers
from .models import Overhead,OverheadType


class OverheadSerializerCreate(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    price = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    payment = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())

    class Meta:
        model = Overhead
        fields = ['id', 'name', 'payment', 'price', 'branch']


class OverheadSerializerGet(serializers.ModelSerializer):
    payment = PaymentTypesSerializers(read_only=True)
    branch = BranchSerializer(read_only=True)

    class Meta:
        model = Overhead
        fields = '__all__'
class OverheadSerializerGetTYpe(serializers.ModelSerializer):

    class Meta:
        model = OverheadType
        fields = '__all__'
