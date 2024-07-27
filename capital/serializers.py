from rest_framework import serializers
from .models import CapitalCategory, Capital
from branch.serializers import BranchSerializer
from branch.models import Branch
from payments.serializers import PaymentTypesSerializers
from payments.models import PaymentTypes


class CapitalCategorySerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    id_number = serializers.CharField(required=False)
    img = serializers.ImageField(required=False)

    class Meta:
        model = CapitalCategory
        fields = ['id', 'name', 'id_number', 'img']


class CapitalSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    id_number = serializers.CharField(required=False)
    price = serializers.IntegerField(required=False)
    total_down_cost = serializers.IntegerField(required=False)
    term = serializers.DateTimeField(required=False)
    curriculum_hours = serializers.IntegerField(required=False)
    img = serializers.ImageField(required=False)
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    payment_type = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=CapitalCategory.objects.all())

    class Meta:
        model = Capital
        fields = ['id', 'name', 'id_number', 'price', 'total_down_cost', 'term',
                  'curriculum_hours', 'img', 'branch', 'payment_type', 'category']

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        return instance


class CapitalListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    id_number = serializers.CharField(required=False)
    price = serializers.IntegerField(required=False)
    total_down_cost = serializers.IntegerField(required=False)
    term = serializers.DateTimeField(required=False)
    curriculum_hours = serializers.IntegerField(required=False)
    img = serializers.ImageField(required=False)
    branch = BranchSerializer(required=False)
    payment_type = PaymentTypesSerializers(required=False)
    category = CapitalCategorySerializers(required=False)

    class Meta:
        model = Capital
        fields = ['id', 'name', 'id_number', 'price', 'total_down_cost', 'term',
                  'curriculum_hours', 'img', 'branch', 'payment_type', 'category']


class CapitalTermSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    down_cost = serializers.IntegerField(required=False)
    month_date = serializers.DateTimeField(required=False)
    capital = serializers.PrimaryKeyRelatedField(queryset=Capital.objects.all())

    class Meta:
        model = Capital
        fields = ['id', 'down_cost', 'month_date', 'capital']


class CapitalTermListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    down_cost = serializers.IntegerField(required=False)
    month_date = serializers.DateTimeField(required=False)
    capital = CapitalSerializers(required=False)

    class Meta:
        model = Capital
        fields = ['id', 'down_cost', 'month_date', 'capital']
