from rest_framework import serializers

from .models import System


class SystemSerializers(serializers.ModelSerializer):
    class Meta:
        model = System
        fields = '__all__'