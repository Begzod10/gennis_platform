from rest_framework import serializers
from django.contrib.auth.models import Group

from permissions.models import Access, ManyBranch, ManyLocation, ManySystem
from system.models import System
from system.serializers import SystemSerializers
from location.serializers import LocationSerializers
from user.serializers import UserSerializerRead
from django.contrib.auth.models import Permission
from user.models import CustomUser
from location.models import Location
from branch.models import Branch


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
    User = UserSerializerRead(read_only=True)

    class Meta:
        model = Access
        fields = ['id', 'group', 'user']


class ManySystemSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    system = serializers.PrimaryKeyRelatedField(queryset=System.objects.all())

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        system = kwargs.pop('system', None)
        super().__init__(*args, **kwargs)
        self.initial_data = {'user': user, 'system': system}

    class Meta:
        model = ManySystem
        fields = ['id', 'user', 'system']

    def create(self, validated_data):
        return ManySystem.objects.create(**validated_data)


class ManyLocationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        system = kwargs.pop('location', None)
        super().__init__(*args, **kwargs)
        self.initial_data = {'user': user, 'location': system}

    class Meta:
        model = ManyLocation
        fields = ['id', 'user', 'location']

    def create(self, validated_data):
        return ManyLocation.objects.create(**validated_data)


class ManyBranchSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    branch = serializers.PrimaryKeyRelatedField(queryset=Branch.objects.all())

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        system = kwargs.pop('branch', None)
        super().__init__(*args, **kwargs)
        self.initial_data = {'user': user, 'branch': system}

    class Meta:
        model = ManyBranch
        fields = ['id', 'user', 'branch']

    def create(self, validated_data):
        return ManyBranch.objects.create(**validated_data)
