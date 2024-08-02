from rest_framework import serializers

from location.serializers import LocationListSerializers, Location
from .models import Branch


class BranchSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
    name = serializers.CharField(max_length=255, required=False)
    number = serializers.IntegerField(required=False)
    map_link = serializers.CharField(required=False)
    code = serializers.IntegerField(required=False)
    phone_number = serializers.CharField(max_length=20, required=False)
    director_fio = serializers.CharField(max_length=255, required=False)
    location_text = serializers.CharField(max_length=255, required=False)
    district = serializers.CharField(max_length=255, required=False)
    bank_sheet = serializers.CharField(required=False)
    inn = serializers.CharField(max_length=255, required=False)
    bank = serializers.CharField(max_length=255, required=False)
    mfo = serializers.CharField(max_length=50, required=False)
    campus_name = serializers.CharField(max_length=255, required=False)
    address = serializers.CharField(max_length=255, required=False)
    year = serializers.DateField(required=False)

    class Meta:
        model = Branch
        fields = ['id', 'name', 'number', 'location', 'map_link', 'code', 'phone_number',
                  'director_fio', 'location_text', 'district', 'bank_sheet', 'inn',
                  'bank', 'mfo', 'campus_name', 'address', 'year']

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


class BranchListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    location = LocationListSerializers(required=False)
    name = serializers.CharField(max_length=255, required=False)
    number = serializers.IntegerField(required=False)
    map_link = serializers.CharField(required=False)
    code = serializers.IntegerField(required=False)
    phone_number = serializers.CharField(max_length=20, required=False)
    director_fio = serializers.CharField(max_length=255, required=False)
    location_text = serializers.CharField(max_length=255, required=False)
    district = serializers.CharField(max_length=255, required=False)
    bank_sheet = serializers.CharField(required=False)
    inn = serializers.CharField(max_length=255, required=False)
    bank = serializers.CharField(max_length=255, required=False)
    mfo = serializers.CharField(max_length=50, required=False)
    campus_name = serializers.CharField(max_length=255, required=False)
    address = serializers.CharField(max_length=255, required=False)
    year = serializers.DateField(required=False)

    class Meta:
        model = Branch
        fields = ['id', 'name', 'number', 'location', 'map_link', 'code', 'phone_number',
                  'director_fio', 'location_text', 'district', 'bank_sheet', 'inn',
                  'bank', 'mfo', 'campus_name', 'address', 'year']
