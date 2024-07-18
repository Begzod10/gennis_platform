from rest_framework import generics
from rest_framework.response import Response

from permissions.functions.CheckUserPermissions import check_user_permissions
from user.functions.functions import check_auth
from .serializers import (Language, LanguageSerializers)


class CreateLanguageList(generics.ListCreateAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializers

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['language']
        permissions = check_user_permissions(user, table_names)

        queryset = Language.objects.all()
        serializer = LanguageSerializers(queryset, many=True)
        return Response({'languages': serializer.data, 'permissions': permissions})

class LanguageRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializers  # permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly) # login qilgan yoki yuq ligini va admin emasligini tekshiradi
