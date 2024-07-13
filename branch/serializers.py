from rest_framework import serializers

from location.serializers import LocationSerializers, Location
from .models import Branch


class BranchSerializer(serializers.ModelSerializer):
    location = LocationSerializers(required=False)
    name = serializers.CharField(max_length=100, required=False)
    number = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = Branch
        fields = ['id', 'name', 'number', 'location']

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        location = Location.objects.get(name=location_data['name'])
        branch = Branch.objects.create(**validated_data, location=location)

        return branch

    def update(self, instance, validated_data):
        location_data = validated_data.pop('location', None)
        if location_data:
            location = Location.objects.get(name=location_data['name'])
            instance.location = location

        instance.name = validated_data.get('name', instance.name)
        instance.number = validated_data.get('number', instance.number)
        instance.save()

        return instance
