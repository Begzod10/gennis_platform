from rest_framework import generics
from rest_framework.response import Response

from permissions.functions.CheckUserPermissions import check_user_permissions
from tasks.models import Task
from tasks.serializers import TaskGetSerializer
from user.functions.functions import check_auth


class TaskListView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskGetSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['task', 'auth_group', 'branch']
        permissions = check_user_permissions(user, table_names)

        queryset = Task.objects.all()
        serializer = TaskGetSerializer(queryset, many=True)
        return Response({'tasks': serializer.data, 'permissions': permissions})


class TaskRetrieveView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskGetSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['task', 'auth_group', 'branch']
        permissions = check_user_permissions(user, table_names)
        task = self.get_object()
        task_data = self.get_serializer(task).data
        return Response({'task': task_data, 'permissions': permissions})
