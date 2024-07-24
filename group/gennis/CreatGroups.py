import json

from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from group.functions.createGroup import creat_group
from group.models import Group, GroupReason
from group.serializers import GroupSerializer, GroupReasonSerializers
from students.models import Student
from students.serializers import StudentSerializer
from teachers.serializers import Teacher, TeacherSerializer


class CreateGroupReasonList(generics.ListCreateAPIView):
    queryset = GroupReason.objects.all()
    serializer_class = GroupReasonSerializers


class GroupReasonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GroupReason.objects.all()
    serializer_class = GroupReasonSerializers


class CreatGroups(APIView):
    def post(self, request):
        data = json.loads(request.body)
        group = creat_group(data.get('students'), data.get('teacher'), data['name'],
                            data['price'], data['branch'], data['language'],
                            data['teacher_salary'], data['attendance_days'],
                            data['level'], data['subject'], data['system'], data['color'], data['class_number'])
        serializers = GroupSerializer(group)
        return Response({'data': serializers.data})

    def get(self, request):
        groups = Group.objects.all()
        serializers = GroupSerializer(groups, many=True)

        return Response(serializers.data)
