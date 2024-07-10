from rest_framework.views import APIView
import json
from rest_framework.response import Response

from time_table.models import GroupTimeTable

from time_table.serializers import GroupTimeTableSerializer
from time_table.functions.checkTime import check_time


class GroupTimeTableUpdate(APIView):

    def patch(self, request, pk):
        data = json.loads(request.body)
        result = check_time(data['group']['id'], data['week']['id'], data['room']['id'], data['branch']['id'],
                            data['start_time'], data['end_time'])
        if result == True:
            instance = GroupTimeTable.objects.get(pk=pk)
            serializer = GroupTimeTableSerializer(data=data, instance=instance)
            serializer.is_valid()
            serializer.save()
            return Response({"data": serializer.data})
        else:
            return Response(result)
