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
from .models import AuthGroupSystem
from branch.serializers import BranchListSerializer


class PermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'content_type_id', 'codename']


class GroupSerializer(serializers.ModelSerializer):
    # permissions = PermissionsSerializer(read_only=True, many=True)

    class Meta:
        model = Group
        fields = ['id', 'name']


class AuthGroupSystemSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True)
    system_id = SystemSerializers(read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = AuthGroupSystem
        fields = ['id', 'group', 'system_id', 'status']

    def get_status(self, obj):
        status = False if Access.objects.filter(auth_group_system=obj).exists() else True
        return status


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
        instance, created = ManySystem.objects.get_or_create(**validated_data)
        return instance


class ManySystemRead(serializers.ModelSerializer):
    user = UserSerializerRead(read_only=True)
    system = SystemSerializers(read_only=True)

    class Meta:
        model = ManySystem
        fields = ['id', 'user', 'system']


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
        instance, created = ManyLocation.objects.get_or_create(**validated_data)
        return instance


class ManyLocationRead(serializers.ModelSerializer):
    user = UserSerializerRead(read_only=True)
    location = LocationSerializers(read_only=True)

    class Meta:
        model = ManyLocation
        fields = ['id', 'user', 'location']


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
        instance, created = ManyBranch.objects.get_or_create(**validated_data)
        return instance


class ManyBranchRead(serializers.ModelSerializer):
    user = UserSerializerRead(read_only=True)
    branch = BranchListSerializer(read_only=True)

    class Meta:
        model = ManyLocation
        fields = ['id', 'user', 'branch']
