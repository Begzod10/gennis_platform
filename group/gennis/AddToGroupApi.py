import json

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from group.models import Group
from students.models import Student

from group.serializers import GroupSerializer, GroupCreateUpdateSerializer
from students.serializers import StudentSerializer


class AddToGroupApi(generics.RetrieveUpdateAPIView):
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
