from rest_framework import serializers

from .models import ClassNumber, ClassTypes, ClassColors


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
