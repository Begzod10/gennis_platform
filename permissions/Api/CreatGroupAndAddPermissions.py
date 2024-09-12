import json

from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from rest_framework.response import Response
from rest_framework.views import APIView

from system.models import System
from system.serializers import SystemSerializers
from .functions.PlatformTables import platform_tables
from ..models import AuthGroupSystem
from ..serializers import GroupSerializer, AuthGroupSystemSerializer


class AddPermissions(APIView):
    def post(self, request, pk):
        data = json.loads(request.body)
        group = Group.objects.get(pk=pk)
        for permission in data['permissions']:
            permission = Permission.objects.get(pk=permission['id'])
            group.permissions.add(permission)

        return Response({'job': group.name, 'permissions': [{
            'name': pms.name,
            'content_type_id': pms.content_type_id,
            'codename': pms.codename
        } for pms in group.permissions.all()]})

    def get(self, request):
        return Response({'tables': platform_tables()})


class JobProfile(APIView):
    def post(self, request, pk):
        data = json.loads(request.body)
        group = Group.objects.get(pk=pk)
        for permission in data['permissions']:
            permission = Permission.objects.get(pk=permission)
            group.permissions.add(permission)

        return Response({'job': group.name, 'permissions': [{
            'name': pms.name,
            'content_type_id': pms.content_type_id,
            'codename': pms.codename
        } for pms in group.permissions.all()]})

    def delete(self, request, pk):
        data = json.loads(request.body)
        group = Group.objects.get(pk=pk)
        permission = Permission.objects.get(pk=data['id'])
        group.permissions.remove(permission)
        return Response({'job': group.name, 'permissions': [{
            'name': pms.name,
            'content_type_id': pms.content_type_id,
            'codename': pms.codename
        } for pms in group.permissions.all()]})

    def get(self, request, pk):
        auth_group_systems = AuthGroupSystem.objects.filter(group_id=pk)
        groups_serializers = AuthGroupSystemSerializer(auth_group_systems, many=True)
        return Response({'job': groups_serializers.data})


class Jobs(APIView):
    def post(self, request):
        data = json.loads(request.body)



        group, created = Group.objects.get_or_create(name=data['name'])

        AuthGroupSystem.objects.create(group_id=group.pk, system_id_id=data['system_id'])
        serializers = GroupSerializer(group)
        return Response({'job': serializers.data})

    def get(self, request):
        systems = System.objects.all()
        serializers = SystemSerializers(systems, many=True)
        groups = Group.objects.all()
        group_ids = [group.pk for group in groups]
        auth_group_systems = AuthGroupSystem.objects.filter(group_id__in=group_ids)
        groups_serializers = AuthGroupSystemSerializer(auth_group_systems, many=True)
        return Response({'systems': serializers.data, 'jobs': groups_serializers.data})


class EditJob(APIView):
    def put(self, request, pk):
        data = json.loads(request.body)
        group = Group.objects.get(pk=pk)
        group.name = data['name']
        group.save()
        gr = AuthGroupSystem.objects.get(group_id=group.pk)
        gr.system_id_id = data['system_id']
        gr.save()

        return Response({'job': group.name})


from permissions.response import CustomResponseMixin


class DeleteJob(CustomResponseMixin, APIView):
    def delete(self, request, pk):
        group = AuthGroupSystem.objects.get(pk=pk)
        group.delete()
        return Response({'success': 'True'})
