from rest_framework import serializers

from .models import Branch
from location.serializers import LocationSerializers


class BranchSerializer(serializers.ModelSerializer):
    location = LocationSerializers()

    class Meta:
        model = Branch
        fields = ['id', 'name', 'number', 'location']

# class BranchSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = Branch
#         fields = '__all__'
