from rest_framework import serializers
from .models import Overhead
from payments.serializers import PaymentTypesSerializers, PaymentTypes


class OverheadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    price = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    payment = PaymentTypesSerializers(required=False)

    class Meta:
        model = Overhead
        fields = ['id', 'name', 'payment', 'price']

    def create(self, validated_data):
        payment = validated_data.pop('payment')
        payment = PaymentTypes.objects.get(name=payment['name'])
        overhead = Overhead.objects.create(**validated_data, payment=payment)
        return overhead

    def update(self, instance, validated_data):
        payment_data = validated_data.pop('payment')
        payment = PaymentTypes.objects.get(name=payment_data['name'])

        instance.name = validated_data.get('name', instance.name)
        instance.created = validated_data.get('created', instance.created)
        instance.payment = payment
        instance.price = validated_data.get('price', instance.price)

        instance.save()
        return instance
