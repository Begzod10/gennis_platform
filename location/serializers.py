from rest_framework import serializers

from .models import Location
from system.serializers import SystemSerializers


class LocationSerializers(serializers.ModelSerializer):
    # system = SystemSerializers(read_only=True)

    class Meta:
        model = Location
        fields = ['id', 'name', 'number', 'system']
