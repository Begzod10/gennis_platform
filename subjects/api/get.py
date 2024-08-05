from rest_framework import generics
from user.functions.functions import check_auth
from rest_framework.response import Response
from subjects.models import SubjectLevel
from subjects.serializers import SubjectLevelListSerializer
from permissions.functions.CheckUserPermissions import check_user_permissions


class SubjectLevelListAPIView(generics.ListAPIView):
    queryset = SubjectLevel.objects.all()
    serializer_class = SubjectLevelListSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['subjectlevel', 'subject']
        permissions = check_user_permissions(user, table_names)

        queryset = SubjectLevel.objects.all()
        serializer = SubjectLevelListSerializer(queryset, many=True)
        return Response({'subjectlevels': serializer.data, 'permissions': permissions})


class SubjectLevelRetrieveAPIView(generics.RetrieveAPIView):
    queryset = SubjectLevel.objects.all()
    serializer_class = SubjectLevelListSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['subjectlevel', 'subject']
        permissions = check_user_permissions(user, table_names)
        subject_level = self.get_object()
        subject_level_data = self.get_serializer(subject_level).data
        return Response({'subjectlevel': subject_level_data, 'permissions': permissions})
