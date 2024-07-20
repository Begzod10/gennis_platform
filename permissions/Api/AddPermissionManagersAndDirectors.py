import json

from rest_framework.views import APIView
from rest_framework.response import Response

from .functions.PlatformTables import platform_tables

from ..models import DescriptionForTable, AuthGroupSystem
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

from system.models import System

from system.serializers import SystemSerializers
from user.models import CustomUser

from ..models import ManySystem, ManyBranch, ManyLocation
from ..serializers import ManySystemSerializer, ManyLocationSerializer, ManyBranchSerializer


class AddPermissionManagersAndDirectors(APIView):
    def post(self, request):
        data = json.loads(request.body)
        for key in ['locations', 'branchs', 'systems']:
            if key in data:
                for item in data[key]:
                    serializer = globals()[f'Many{key.capitalize()[:-1]}Serializer'](user=data['user'],
                                                                                     **{key[:-1]: item})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
        return Response({'message': 'Dostuplar muvaffaqqiyatli berildi!'})
