from rest_framework import generics
from .models import Task
from .serializers import TaskSerializer
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


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
