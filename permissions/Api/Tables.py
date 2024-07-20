import json

from rest_framework.views import APIView
from rest_framework.response import Response

from .functions.PlatformTables import platform_tables
from .functions.PermissionsForTable import get_permissions_for_table


class Tables(APIView):
    def post(self, request):
        data = json.loads(request.body)
        return Response({'permissions': get_permissions_for_table(data['table'])})

    def get(self, request):
        return Response({'tables': platform_tables()})
