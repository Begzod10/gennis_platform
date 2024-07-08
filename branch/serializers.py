from rest_framework import serializers

from .models import Branch
from location.serializers import LocationSerializers


class BranchSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=100, required=True)
    name = serializers.CharField(max_length=100, required=False)
    number = serializers.CharField(max_length=100, required=False)

    location = LocationSerializers(required=False)

    class Meta:
        model = Branch
        fields = ['id', 'name', 'number', 'location']

# class BranchSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = Branch
#         fields = '__all__'
