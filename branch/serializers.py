from rest_framework import serializers

from .models import Branch
from location.serializers import LocationSerializers


class BranchSerializer(serializers.ModelSerializer):
<<<<<<< HEAD
    location = LocationSerializers(read_only=True)
=======
    id = serializers.CharField(max_length=100, required=True)
    name = serializers.CharField(max_length=100, required=False)
    number = serializers.CharField(max_length=100, required=False)

    location = LocationSerializers(required=False)
>>>>>>> 55b1efb65c1279aeaf68712f2b77d013d9849438

    class Meta:
        model = Branch
        fields = ['id', 'name', 'number', 'location']
<<<<<<< HEAD
=======

# class BranchSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = Branch
#         fields = '__all__'
>>>>>>> 55b1efb65c1279aeaf68712f2b77d013d9849438
