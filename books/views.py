from rest_framework import generics
from .models import Book, BookImage
from .serializers import BookSerializer
from user.functions.functions import check_auth
from rest_framework.response import Response
from permissions.functions.CheckUserPermissions import check_user_permissions


class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['book']
        permissions = check_user_permissions(user, table_names)

        queryset = Book.objects.all()
        serializer = BookSerializer(queryset, many=True)
        return Response({'books': serializer.data, 'permissions': permissions})


class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def retrieve(self, request, *args, **kwargs):
        user, auth_error = check_auth(request)
        if auth_error:
            return Response(auth_error)

        table_names = ['book']
        permissions = check_user_permissions(user, table_names)
        book = self.get_object()
        book_data = self.get_serializer(book).data
        return Response({'book': book_data, 'permissions': permissions})
