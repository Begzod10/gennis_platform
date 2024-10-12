from datetime import datetime

from rest_framework import serializers
from rest_framework_simplejwt.authentication import JWTAuthentication

from branch.models import Branch
from branch.serializers import BranchSerializer
from payments.models import PaymentTypes
from payments.serializers import PaymentTypesSerializers
from user.serializers import CustomUser, UserSerializerRead
from .models import CapitalCategory, Capital, OldCapital


class CapitalCategorySerializers(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    id_number = serializers.CharField(required=True)
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
    term = serializers.IntegerField(required=False)
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
    term = serializers.IntegerField(required=False)
    curriculum_hours = serializers.IntegerField(required=False)
    img = serializers.ImageField(required=False)
    branch = BranchSerializer(required=False)
    payment_type = PaymentTypesSerializers(required=False)
    category = CapitalCategorySerializers(required=False)
    date = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Capital
        fields = ['id', 'name', 'id_number', 'price', 'total_down_cost', 'term',
                  'curriculum_hours', 'img', 'branch', 'payment_type', 'category', 'date']

    def get_date(self, obj):
        return obj.added_date.strftime('%Y-%m-%d')


class CapitalTermSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    down_cost = serializers.IntegerField(required=False)
    month_date = serializers.DateField(required=False)
    capital = serializers.PrimaryKeyRelatedField(queryset=Capital.objects.all())

    class Meta:
        model = Capital
        fields = ['id', 'down_cost', 'month_date', 'capital']


class CapitalTermListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    down_cost = serializers.IntegerField(required=False)
    month_date = serializers.DateField(required=False)
    capital = CapitalSerializers(required=False)

    class Meta:
        model = Capital
        fields = ['id', 'down_cost', 'month_date', 'capital']


class OldCapitalSerializers(serializers.ModelSerializer):
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())
    payment_type = serializers.PrimaryKeyRelatedField(queryset=PaymentTypes.objects.all())
    by_who = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=False, allow_null=True)
    added_date = serializers.DateField(required=False)
    day = serializers.CharField(required=False, write_only=True)
    month = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = OldCapital
        fields = '__all__'

    def create(self, validated_data):
        month = int(validated_data.pop('month'))
        day = int(validated_data.pop('day'))
        current_year = datetime.now().year
        date = datetime(year=current_year, month=month, day=day).date()

        jwt_auth = JWTAuthentication()
        request = self.context['request']
        header = request.META.get('HTTP_AUTHORIZATION')
        if header is not None:
            raw_token = header.split(' ')[1]
            validated_token = jwt_auth.get_validated_token(raw_token)
            user_id = validated_token['user_id']
            validated_data['by_who_id'] = user_id
        return OldCapital.objects.create(**validated_data, added_date=date)


class OldCapitalListSerializers(serializers.ModelSerializer):
    by_who = UserSerializerRead(read_only=True)
    branch = BranchSerializer(required=False)
    payment_type = PaymentTypesSerializers(required=False)
    added_date = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OldCapital
        fields = ['id', 'by_who', 'branch', 'payment_type', 'added_date', 'price', 'name']

    def get_added_date(self, obj):
        return obj.added_date.strftime('%Y-%m-%d')
