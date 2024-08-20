from rest_framework import serializers

from system.serializers import SystemSerializers, System
from .models import Location


class LocationSerializers(serializers.ModelSerializer):
    system = serializers.PrimaryKeyRelatedField(queryset=System.objects.all())

    class Meta:
        model = Location
        fields = '__all__'


class LocationListSerializers(serializers.ModelSerializer):
    system = SystemSerializers(read_only=True)

    class Meta:
        model = Location
        fields = ['id', 'name', 'number', 'system']
