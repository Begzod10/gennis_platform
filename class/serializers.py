from rest_framework import serializers

from .models import ClassNumber, ClassTypes, ClassColors, ClassCoin, StudentCoin, CoinInfo


class ClassNumberSerializers(serializers.ModelSerializer):
    class Meta:
        model = ClassNumber
        fields = '__all__'


class ClassTypesSerializers(serializers.ModelSerializer):
    class Meta:
        model = ClassTypes
        fields = '__all__'


class ClassColorsSerializers(serializers.ModelSerializer):
    class Meta:
        model = ClassColors
        fields = '__all__'


class ClassCoinSerializers(serializers.ModelSerializer):
    class Meta:
        model = ClassCoin
        fields = '__all__'


class StudentCoinSerializers(serializers.ModelSerializer):
    class Meta:
        model = StudentCoin
        fields = '__all__'


class CoinInfoSerializers(serializers.ModelSerializer):
    class Meta:
        model = CoinInfo
        fields = '__all__'
