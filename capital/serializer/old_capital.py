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

class OldCapitalsListSerializersTotal(serializers.ModelSerializer):
    student_id = serializers.CharField(source='by_who.id',
                                       read_only=True)
    name = serializers.CharField(source='by_who.name',
                                         read_only=True)
    surname = serializers.CharField(source='by_who.surname',
                                            read_only=True)
    payment_type_name = serializers.CharField(source='payment_type.name',
                                              read_only=True)
    payment_sum = serializers.IntegerField(required=False,source='price')
    status = serializers.BooleanField(required=False)
    date=serializers.DateField(required=False,source='added_date')
    capital = serializers.CharField(source='name')

    class Meta:
        model = OldCapital
        fields = ['id', 'name', 'surname', 'payment_type_name', 'payment_sum', 'status', 'added_date',
                  'date',"student_id","capital"]
