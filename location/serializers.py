from rest_framework import serializers

from system.serializers import SystemSerializers, System
from .models import Location


class LocationSerializers(serializers.ModelSerializer):
    system = SystemSerializers(required=False)
    name = serializers.CharField(max_length=255, required=False)
    number = serializers.IntegerField(required=False)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Location
        fields = ['id', 'name', 'number', 'system']

    def create(self, validated_data):
        system_data = validated_data.pop('system')

        system = System.objects.get(name=system_data['name'])
        location = Location.objects.create(**validated_data, system=system)
        return location

    def update(self, instance, validated_data):
        system_data = validated_data.pop('system', None)
        if system_data:
            system = System.objects.get(name=system_data['name'])
            instance.system = system

        instance.name = validated_data.get('name', instance.name)
        instance.number = validated_data.get('number', instance.number)
        instance.save()

        return instance
