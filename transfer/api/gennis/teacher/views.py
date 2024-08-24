from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from teachers.models import Teacher
from transfer.api.gennis.teacher.serializers import (
    TeacherSerializerTransfer, TeacherBranchSerializer
)


class TeacherCreateView(generics.CreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializerTransfer


class TeacherBranchCreateView(generics.GenericAPIView):
    serializer_class = TeacherBranchSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            teacher = serializer.save()
            return Response({'status': 'branch added', 'teacher_id': teacher.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
