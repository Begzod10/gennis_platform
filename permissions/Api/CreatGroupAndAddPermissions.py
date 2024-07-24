import json

from rest_framework.views import APIView
from rest_framework.response import Response

from .functions.PlatformTables import platform_tables

from ..models import DescriptionForTable, AuthGroupSystem
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

from system.models import System

from system.serializers import SystemSerializers


class CreatGroupAndAddPermissions(APIView):
    def post(self, request):
        data = json.loads(request.body)
        group = Group.objects.create(name=data['name'])
        AuthGroupSystem.objects.create(group_id=group.pk, system_id_id=data['system_id'])
        for permission in data['permissions']:
            permission = Permission.objects.get(pk=permission['id'])
            group.permissions.add(permission)

        return Response({'job': group.name, 'permissions': [{
            'name': pms.name,
            'content_type_id': pms.content_type_id,
            'codename': pms.codename
        } for pms in group.permissions.all()]})

    def get(self, request):
        systems = System.objects.all()
        serializers = SystemSerializers(systems, many=True)
        return Response({'tables': platform_tables(), 'systems': serializers.data})
