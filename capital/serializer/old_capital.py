from rest_framework import serializers
from capital.models import OldCapital


class OldCapitalsListSerializers(serializers.ModelSerializer):
    by_who = serializers.SerializerMethodField(required=False)
    payment_type = serializers.SerializerMethodField(required=False)

    class Meta:
        model = OldCapital
        fields = ['id', 'by_who', 'payment_type', 'added_date', 'price', 'name']

    def get_by_who(self, obj):
        return f"{obj.by_who.name} {obj.by_who.surname} {obj.by_who.father_name}"

    def get_payment_type(self, obj):
        return obj.payment_type.name
