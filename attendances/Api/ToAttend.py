from rest_framework.views import APIView
from rest_framework.response import Response
from group.models import Group
from students.serializers import StudentSerializer
import jwt
import json
import calendar
from .functions.CheckAndCreateAttendancePerMonth import check_and_create_attendance_per_month


class ToAttend(APIView):
    def post(self, request, group_id):
        data = json.loads(request.body)
        return Response(check_and_create_attendance_per_month(group_id, students=data['students'], date=data['date']))

    def get(self, request, group_id):
        group = Group.objects.get(pk=group_id)
        serializer = StudentSerializer(group.students.all(), many=True)
        return Response({'students': serializer.data})


