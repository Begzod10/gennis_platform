from rest_framework import serializers

from .models import Branch
from location.serializers import LocationSerializers


class BranchSerializer(serializers.ModelSerializer):
    location = LocationSerializers(read_only=True)

    class Meta:
        model = Branch
        fields = ['id', 'name', 'number', 'location']
