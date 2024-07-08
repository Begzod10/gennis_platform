from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

import jwt
import json

# from students.models import Student
# from group.models import Group

from teachers.models import Teacher
from students.serializers import StudentSerializer, Student
from group.serializers import GroupSerializer, Group
from user.models import CustomUser


class CreatGroups(APIView):
    # def post(self, request):
    #     data = json.loads(request.body)
    #     students = data.get('students')
    #     teacher = data.get('teacher')
    #     group = Group.objects.create(name=data['name'], price=data['price'], branch_id=data['branch'],
    #                                  language_id=data['language'], teacher_salary=data['teacher_salary'],
    #                                  attendance_days=data['attendance_days'], status=False, deleted=False,
    #                                  level_id=data['level'], subject_id=data['subject'])
    #     for student in students:
    #         st = Student.objects.get(pk=student)
    #         group.students.add(st)
    #     tch = Teacher.objects.get(pk=teacher)
    #     group.teacher.add(tch)
    #     serializers = GroupSerializer(group)
    #     return Response({'data': serializers.data})
    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save()
            return Response({'data': GroupSerializer(group).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        groups = Group.objects.all()
        serializers = GroupSerializer(groups, many=True)
        return Response(serializers.data)


class GroupProfile(generics.RetrieveUpdateAPIView):
    queryset = Group
    serializer_class = GroupSerializer


class DeleteGroups(APIView):
    def post(self, request, pk):
        group = Group.objects.get(pk=pk)
        group.deleted = True
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})

    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})


class AddToGroupApi(APIView):
    def post(self, request, pk):
        group = Group.objects.get(pk=pk)
        data = json.loads(request.body)
        students = data.get('students')
        for student in students:
            st = Student.objects.get(pk=student)
            group.students.add(st)
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})

    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        group_serializer = GroupSerializer(group)
        if group.branch.name == "Gennis":
            students = Student.objects.filter(user__branch_id=group.branch_id, subject_id=group.subject_id)
            serializers = StudentSerializer(students, many=True)
            return Response({'students': serializers.data, 'group': group_serializer.data})
        else:
            students = Student.objects.filter(user__branch_id=group.branch_id)
            serializers = StudentSerializer(students, many=True)
            return Response({'data': serializers.data, 'group': group_serializer.data})


class MoveToGroupApi(APIView):
    def post(self, request, pk):
        group = Group.objects.get(pk=pk)
        data = json.loads(request.body)
        to_group_id = data.get('to_group_id')
        to_group = Group.objects.get(pk=to_group_id)
        students = data.get('students')
        for student in students:
            st = Student.objects.get(pk=student)
            to_group.students.add(st)
        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})

    def get(self, request, pk):
        group = Group.objects.get(pk=pk)
        group_serializer = GroupSerializer(group)
        groups = Group.objects.filter(branch_id=group.branch_id, system_id=group.system_id)
        groups_serializers = GroupSerializer(groups, many=True)
        return Response({'groups': groups_serializers.data, 'group': group_serializer.data})

# class

