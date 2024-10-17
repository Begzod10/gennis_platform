from rest_framework import serializers
from overhead.models import Overhead


class ActiveListTeacherSerializer(serializers.ModelSerializer):
    payment = serializers.SerializerMethodField(required=False)
    created = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Overhead
        fields = ('id', 'name', 'price', 'created', 'payment')

    def get_payment(self, obj):
        return obj.payment.name

    def get_created(self, obj):
        return obj.created.strftime('%Y-%m-%d')
