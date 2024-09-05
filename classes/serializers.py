from rest_framework import serializers

from group.models import Group
from group.serializers import GroupSerializer
from students.models import Student
from students.serializers import StudentSerializer
from subjects.models import Subject
from subjects.serializers import SubjectSerializer
from .models import ClassNumber, ClassTypes, ClassColors, ClassCoin, StudentCoin, CoinInfo


class ClassTypesSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)

    class Meta:
        model = ClassTypes
        fields = ['id', 'name']


class ClassNumberListSerializers(serializers.ModelSerializer):
    class_types = ClassTypesSerializers(required=False)
    subjects = SubjectSerializer(required=False, many=True)

    class Meta:
        model = ClassNumber
        fields = '__all__'


class ClassNumberSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    number = serializers.IntegerField(required=False)
    price = serializers.IntegerField(required=False)
    curriculum_hours = serializers.IntegerField(required=False)
    class_types = serializers.PrimaryKeyRelatedField(queryset=ClassTypes.objects.all(), required=True)
    subjects = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), required=False, allow_null=True, many=True)

    class Meta:
        model = ClassNumber
        fields = ['id', 'number', 'curriculum_hours', 'class_types', 'subjects', 'price']

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        return instance



class ClassColorsSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    value = serializers.CharField(required=False)

    class Meta:
        model = ClassColors
        fields = ['id', 'name', 'value']


class ClassCoinSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    total_coin = serializers.IntegerField(required=False)
    given_coin = serializers.IntegerField(required=False)
    remaining_coin = serializers.IntegerField(required=False)
    month_date = serializers.DateField(required=False)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = ClassCoin
        fields = ['id', 'total_coin', 'given_coin', 'remaining_coin', 'month_date', 'group']


class ClassCoinListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    total_coin = serializers.IntegerField(required=False)
    given_coin = serializers.IntegerField(required=False)
    remaining_coin = serializers.IntegerField(required=False)
    month_date = serializers.DateField(required=False)
    group = GroupSerializer(required=False)

    class Meta:
        model = ClassCoin
        fields = ['id', 'total_coin', 'given_coin', 'remaining_coin', 'month_date', 'group']


class StudentCoinSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    value = serializers.CharField(required=False)
    class_coin = serializers.PrimaryKeyRelatedField(queryset=ClassCoin.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta:
        model = StudentCoin
        fields = ['id', 'value', 'class_coin', 'student']


class StudentCoinListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    value = serializers.CharField(required=False)
    class_coin = ClassCoinSerializers(required=False)
    student = StudentSerializer(required=False)

    class Meta:
        model = StudentCoin
        fields = ['id', 'value', 'class_coin', 'student']


class CoinInfoSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    value = serializers.CharField(required=False)
    reason = serializers.CharField(required=False)
    day_date = serializers.DateField(required=False)
    class_coin = serializers.PrimaryKeyRelatedField(queryset=ClassCoin.objects.all())

    class Meta:
        model = CoinInfo
        fields = ['id', 'value', 'reason', 'day_date', 'class_coin']


class CoinInfoListSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    value = serializers.CharField(required=False)
    reason = serializers.CharField(required=False)
    day_date = serializers.DateField(required=False)
    class_coin = ClassCoinSerializers(required=False)

    class Meta:
        model = CoinInfo
        fields = ['id', 'value', 'reason', 'day_date', 'class_coin']
