import json

from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import status as http_status
from group.models import Group, SubjectLevel
from group.serializers import GroupSerializer, GroupCreateUpdateSerializer
from students.models import Student
from students.serializers import StudentSerializer
from user.serializers import CustomUser, UserSerializerRead


class AddToGroupApi(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Group.objects.all()
    serializer_class = GroupCreateUpdateSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return GroupCreateUpdateSerializer
        return GroupSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance.refresh_from_db()
        read_serializer = GroupSerializer(instance)
        return Response(read_serializer.data)


class AddToGroupApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        students = request.data.get('students', [])

        for student_id in students:
            student = get_object_or_404(Student, pk=student_id)

            # Check for schedule conflict
            conflict = False
            for st_group in student.groups_student.all():
                if (
                        group.group_time_table.start_time == st_group.group_time_table.start_time and
                        group.group_time_table.end_time == st_group.group_time_table.end_time and
                        group.group_time_table.week == st_group.group_time_table.week and
                        group.group_time_table.room == st_group.group_time_table.room
                ):
                    conflict = True
                    break

            if conflict:
                continue  # Skip this student due to conflict

            # Update payment and add to group
            student.total_payment_month += group.price
            student.save()
            group.students.add(student)

        return Response({"message": "Students added successfully"}, status=http_status.HTTP_200_OK)

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


class UpdateGroupDataAPIView(APIView):

    def post(self, request, *args, **kwargs):
        group_data = request.data.get('group', {})
        group = get_object_or_404(Group, id=group_data.get('platform_id'))

        course_data = group_data.get('course')
        if course_data:
            level = SubjectLevel.objects.filter(classroom_id=course_data.get('id')).first()
            if not level:
                level = SubjectLevel.objects.filter(name=course_data.get('name')).first()
            if level:
                group.level_id = level.id
                group.save()

        return Response({"msg": "O'zgarildi"}, status=status.HTTP_200_OK)


class GetGroupDataAPIView(APIView):

    def get(self, request, group_id):
        access_token = str(AccessToken.for_user(request.user))

        group = get_object_or_404(Group, id=group_id)
        group_serializer = GroupSerializer(group)

        students = Student.objects.filter(group_id=group_id).select_related('user')
        user_ids = [student.user.id for student in students if student.user]
        users = CustomUser.objects.filter(id__in=user_ids)
        user_serializer = UserSerializerRead(users, many=True)

        response_data = {
            "users": user_serializer.data,
            "access_token": access_token,
            "group": group_serializer.data
        }

        return Response(response_data)
