from rest_framework import serializers

from overhead.models import Overhead


# class ActiveListTeacherSerializer(serializers.ModelSerializer):
#     payment = serializers.SerializerMethodField(required=False)
#     created = serializers.SerializerMethodField(required=False)
#
#     class Meta:
#         model = Overhead
#         fields = ('id', 'name', 'price', 'created', 'payment')
#
#     def get_payment(self, obj):
#         return obj.payment.name
#
#     def get_created(self, obj):
#         return obj.created.strftime('%Y-%m-%d')
#
#     def to_representation(self, instance):
#         ret = super().to_representation(instance)
#         if not ret['name'] and instance.type:
#             ret['name'] = instance.type.name
#         return ret
class ActiveListTeacherSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='type.name', read_only=True)
    payment_type_name = serializers.CharField(source='payment.name', read_only=True)
    payment_sum = serializers.IntegerField(source='price', required=False)
    status = serializers.BooleanField(required=False, default=False)
    date = serializers.DateField(source='created', required=False)

    class Meta:
        model = Overhead
        fields = [
            'id',
            'name',
            'payment_type_name',
            'payment_sum',
            'status',
            'date',
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        print(ret)
        if not ret['name'] and instance.type or ret['name'] != "Boshqa":
            ret['name'] = instance.type.name
        else:
            ret['name'] = instance.name
        return ret
