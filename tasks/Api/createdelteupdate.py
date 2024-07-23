from rest_framework import generics

from tasks.models import Task
from tasks.serializers import TaskSerializer, StudentCallInfoCreateUpdateDeleteSerializers, StudentCallInfo


class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskUpdateView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskDestroyView(generics.DestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class StudentCallInfoCreateView(generics.CreateAPIView):
    queryset = StudentCallInfo.objects.all()
    serializer_class = StudentCallInfoCreateUpdateDeleteSerializers


class StudentCallInfoDestroyView(generics.DestroyAPIView):
    queryset = StudentCallInfo.objects.all()
    serializer_class = StudentCallInfoCreateUpdateDeleteSerializers


class StudentCallInfoUpdateView(generics.UpdateAPIView):
    queryset = StudentCallInfo.objects.all()
    serializer_class = StudentCallInfoCreateUpdateDeleteSerializers
