from rest_framework import generics
from rest_framework.response import Response

from permissions.functions.CheckUserPermissions import check_user_permissions
from user.functions.functions import check_auth
from .models import Task, StudentCallInfo
from .serializers import TaskSerializer, StudentCallInfoSerializers


class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['task', 'auth_group', 'branch']
        permissions = check_user_permissions(user, table_names)

        queryset = Task.objects.all()
        serializer = TaskSerializer(queryset, many=True)
        return Response({'tasks': serializer.data, 'permissions': permissions})


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['task', 'auth_group', 'branch']
        permissions = check_user_permissions(user, table_names)
        task = self.get_object()
        task_data = self.get_serializer(task).data
        return Response({'task': task_data, 'permissions': permissions})


class StudentCallinfoCreateView(generics.ListCreateAPIView):
    queryset = StudentCallInfo.objects.all()
    serializer_class = StudentCallInfoSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['task', 'student', 'StudentCallInfo']
        permissions = check_user_permissions(user, table_names)

        queryset = StudentCallInfo.objects.all()
        serializer = StudentCallInfoSerializers(queryset, many=True)
        return Response({'tasks': serializer.data, 'permissions': permissions})
