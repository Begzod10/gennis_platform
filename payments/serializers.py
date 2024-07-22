from rest_framework import serializers

from .models import PaymentTypes


class PaymentTypesSerializers(serializers.ModelSerializer):
    class Meta:
        model = PaymentTypes
        fields = '__all__'
