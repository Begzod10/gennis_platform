from rest_framework import serializers

from .models import System


class SystemSerializers(serializers.ModelSerializer):
    name = serializers.CharField(required=False)

    class Meta:
        model = System
        fields = ['id', 'name', 'number']


class SystemSerializersUsers(serializers.ModelSerializer):
    system = SystemSerializers(read_only=True)

    class Meta:
        model = System
        fields = ['system']
