from rest_framework import serializers

from .models import PaymentTypes


class PaymentTypesSerializers(serializers.ModelSerializer):
    old_id = serializers.IntegerField(required=False)

    class Meta:
        model = PaymentTypes
        fields = '__all__'
