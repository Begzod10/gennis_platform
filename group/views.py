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
                            data['level'], data['subject'], data['system'])
        serializers = GroupSerializer(group)
        return Response({'data': serializers.data})

    def get(self, request):
        groups = Group.objects.all()
        serializers = GroupSerializer(groups, many=True)

        return Response(serializers.data)


class GroupProfile(generics.RetrieveUpdateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    # user = CustomUser.objects.get(pk=1)
    # table_names = ['group']
    # check_user_permissions(user, table_names)


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


class TeacherGroupChange(APIView):
    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        data = request.data
        teacher_id = data.get('teacher')

        if not teacher_id:
            return Response({'error': 'Teacher ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        teacher = get_object_or_404(Teacher, pk=teacher_id)
        statuss = False

        if (group.group_time_table.start_time != teacher.group.group_time_table.start_time and
                group.group_time_table.week != teacher.group.group_time_table.week and
                group.group_time_table.room != teacher.group.group_time_table.room and
                group.group_time_table.end_time != teacher.group.group_time_table.end_time):
            statuss = True

        if statuss:
            teacher.group = None
            teacher.save()
            group.teacher.add(teacher)

        serializer = GroupSerializer(group)
        return Response({'data': serializer.data})

    def get(self, request,pk):
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        week = request.query_params.get('week')
        room = request.query_params.get('room')
        teachers = Teacher.objects.all()
        teacher_data = []

        for teacher in teachers:
            status = (start_time != teacher.group.group_time_table.start_time and
                      week != teacher.group.group_time_table.week and
                      room != teacher.group.group_time_table.room and
                      end_time != teacher.group.group_time_table.end_time)
            serializer = TeacherSerializer(teacher)
            data = {
                'teacher': serializer.data,
                'status': status
            }
            teacher_data.append(data)

        return Response(teacher_data)


class AddToGroupApi(APIView):
    def post(self, request, pk):
        group = Group.objects.get(pk=pk)
        data = json.loads(request.body)
        students = data.get('students')
        for student in students:
            st = Student.objects.get(pk=student)
            st.total_payment_month += group.price
            st.save()
            status = False
            for st_group in student.groups_student:
                if group.group_time_table.start_time != st_group.group_time_table.start_time and group.group_time_table.week != st_group.group_time_table.week and group.group_time_table.room != st_group.group_time_table.room and group.group_time_table.end_time != st_group.group_time_table.end_time:
                    status = True
            if status:
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
