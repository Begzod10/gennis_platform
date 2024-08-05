from rest_framework import serializers

from system.serializers import SystemSerializers, System
from .models import Location


class LocationSerializers(serializers.ModelSerializer):
    system = serializers.PrimaryKeyRelatedField(queryset=System.objects.all(), required=False)
    name = serializers.CharField(max_length=255, required=False)
    number = serializers.CharField(required=False)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Location
        fields = ['id', 'name', 'number', 'system', 'old_id']


class LocationListSerializers(serializers.ModelSerializer):
    system = SystemSerializers(required=False)
    name = serializers.CharField(max_length=255, required=False)
    number = serializers.IntegerField(required=False)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Location
        fields = ['id', 'name', 'number', 'system']
