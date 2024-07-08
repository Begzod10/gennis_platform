from rest_framework import serializers

from .models import Branch
from location.serializers import LocationSerializers


class BranchSerializer(serializers.ModelSerializer):
    location = LocationSerializers()

    class Meta:
        model = Branch
        fields = ['id', 'name', 'number', 'location']
<<<<<<< HEAD
=======

# class BranchSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = Branch
#         fields = '__all__'
>>>>>>> 2398607749231d583f9f93f6743201907f04addb
