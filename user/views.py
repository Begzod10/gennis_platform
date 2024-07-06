from user.serializers import UserSerializer, CustomUser, UserSalaryListSerializers
from rest_framework import generics


class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserSalaryListListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSalaryListSerializers


class UserSalaryListDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSalaryListSerializers
