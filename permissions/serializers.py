from rest_framework import serializers
from django.contrib.auth.models import Group

from permissions.models import Access, ManyBranch, ManyLocation, ManySystem
from system.serializers import SystemSerializers
from location.serializers import LocationSerializers
from user.serializers import UserSerializer
from django.contrib.auth.models import Permission


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class PermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'content_type_id', 'codename']


class AuthGroupSystemSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)
    system = SystemSerializers(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'group', 'system']


class AccessSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)
    system = SystemSerializers(read_only=True)
    User = UserSerializer(read_only=True)

    class Meta:
        model = Access
        fields = ['id', 'group', 'user']


class ManySystemSerializer(serializers.ModelSerializer):
    access = AccessSerializer(read_only=True)
    system = SystemSerializers(read_only=True)

    class Meta:
        model = ManySystem
        fields = ['id', 'access', 'system']


class ManyLocationSerializer(serializers.ModelSerializer):
    access = AccessSerializer(read_only=True)
    location = LocationSerializers(read_only=True)

    class Meta:
        model = ManyLocation
        fields = ['id', 'access', 'location']


class ManyBranchSerializer(serializers.ModelSerializer):
    access = AccessSerializer(read_only=True)
    location = LocationSerializers(read_only=True)

    class Meta:
        model = ManyBranch
        fields = ['id', 'access', 'location']
