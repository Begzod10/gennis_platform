import json

from rest_framework.views import APIView
from rest_framework.response import Response

from .functions.PlatformTables import platform_tables

from ..models import DescriptionForTable


class DescriptionTables(APIView):
    def post(self, request):
        data = json.loads(request.body)
        description = DescriptionForTable.objects.create(table_name=data['table'], description=data['description'])
        return Response({'table': description.table_name, 'description': description.description})

    def get(self, request):
        return Response({'tables': platform_tables()})
