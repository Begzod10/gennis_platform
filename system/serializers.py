from rest_framework import serializers

from .models import System


class SystemSerializers(serializers.ModelSerializer):
    name = serializers.CharField(required=False)

    class Meta:
        model = System
        fields = '__all__'
