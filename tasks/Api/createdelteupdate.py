from rest_framework import generics

from tasks.models import Task
from tasks.serializers import TaskSerializer, StudentCallInfoCreateUpdateDeleteSerializers, StudentCallInfo
from rest_framework.permissions import IsAuthenticated

class TaskCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class StudentCallInfoCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = StudentCallInfo.objects.all()
    serializer_class = StudentCallInfoCreateUpdateDeleteSerializers


class StudentCallInfoDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = StudentCallInfo.objects.all()
    serializer_class = StudentCallInfoCreateUpdateDeleteSerializers


class StudentCallInfoUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = StudentCallInfo.objects.all()
    serializer_class = StudentCallInfoCreateUpdateDeleteSerializers



