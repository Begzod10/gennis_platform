from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from group.models import Group
from students.serializers import StudentSerializer
import jwt
import json
import calendar
from .functions.CheckAndCreateAttendancePerMonth import check_and_create_attendance_per_month
from ..serializers import AttendancePerDaySerializer, AttendancePerDayCreateUpdateSerializer
from ..models import AttendancePerDay


# class ToAttend(APIView):
#     def post(self, request, group_id):
#         data = json.loads(request.body)
#         return Response(check_and_create_attendance_per_month(group_id, students=data['students'], date=data['date']))
#
#     def get(self, request, group_id):
#         group = Group.objects.get(pk=group_id)
#         serializer = StudentSerializer(group.students.all(), many=True)
#         return Response({'students': serializer.data})


class ToAttend(generics.ListCreateAPIView):
    serializer_class = AttendancePerDayCreateUpdateSerializer

    def get_queryset(self):
        id = self.request.query_params.get('id')
        if id is not None:
            return AttendancePerDay.objects.filter(group_id=id)
        return AttendancePerDay.objects.all()


