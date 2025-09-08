from rest_framework import serializers

from .models import Test,Term


class TestCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = '__all__'
class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = '__all__'