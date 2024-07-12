from rest_framework import serializers

from .models import Branch
from location.serializers import Location


class BranchSerializer(serializers.ModelSerializer):
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
    name = serializers.CharField(max_length=100, required=False)
    number = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = Branch
        fields = ['id', 'name', 'number', 'location']
