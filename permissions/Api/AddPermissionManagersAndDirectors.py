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
from branch.models import Branch
from branch.serializers import BranchSerializer
from location.models import Location
from location.serializers import LocationSerializers


class AddPermissionManagersAndDirectors(APIView):
    def post(self, request):
        print(request.body)
        data = json.loads(request.body)
        print(data)
        for key in ['locations', 'branchs', 'systems']:
            print(key)
            if key in data:
                print(True)
                for item in data[key]:
                    serializer = globals()[f'Many{key.capitalize()[:-1]}Serializer'](user=data['user'],
                                                                                     **{key[:-1]: item})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    print(serializer.data)
        return Response({'message': 'Dostuplar muvaffaqqiyatli berildi!'})

    def get(self, request):
        systems = System.objects.all()
        system_serializer = SystemSerializers(systems, many=True)
        branches = Branch.objects.all()
        branches_serializer = BranchSerializer(branches, many=True)
        locations = Location.objects.all()
        locations_serializer = LocationSerializers(locations, many=True)
        return Response({'systems': system_serializer.data, 'branches': branches_serializer.data,
                         'locations': locations_serializer.data})
