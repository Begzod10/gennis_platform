from rest_framework import serializers

from .models import ClassNumber, ClassTypes, ClassColors, ClassCoin, StudentCoin, CoinInfo
from subjects.serializers import SubjectSerializer
from group.serializers import GroupSerializer
from students.serializers import StudentSerializer


class ClassTypesSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)

    class Meta:
        model = ClassTypes
        fields = ['id', 'name']


class ClassNumberSerializers(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    number = serializers.IntegerField(required=False)
    curriculum_hours = serializers.IntegerField(required=False)
    class_types = ClassTypesSerializers(required=False)
    subjects = SubjectSerializer(required=False)

    class Meta:
        model = ClassNumber
        fields = ['id', 'number', 'curriculum_hours', 'class_types', 'subjects']


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
    group = GroupSerializer(required=False)

    class Meta:
        model = ClassCoin
        fields = ['id', 'total_coin', 'given_coin', 'remaining_coin', 'month_date', 'group']


class StudentCoinSerializers(serializers.ModelSerializer):
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
    class_coin = ClassCoinSerializers(required=False)

    class Meta:
        model = CoinInfo
        fields = ['id', 'value', 'reason', 'day_date', 'class_coin']
