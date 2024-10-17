from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from user.models import CustomUser, UserSalaryList
from user.serializers import UserSerializerWrite, UserSalaryListSerializers, CustomTokenObtainPairSerializer


class UserCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializerWrite


class UserUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializerWrite


class UserDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializerWrite


class UserSalaryListCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = UserSalaryList.objects.all()
    serializer_class = UserSalaryListSerializers


class UserSalaryListUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = UserSalaryList.objects.all()
    serializer_class = UserSalaryListSerializers


class UserSalaryListDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = UserSalaryList.objects.all()
    serializer_class = UserSalaryListSerializers

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = True
        instance.save()

        user_salary = instance.user_salary
        user_salary.taken_salary -= instance.salary
        user_salary.remaining_salary += instance.salary
        user_salary.save()

        return Response({"msg": " salary deleted successfully"}, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UsernameCheck(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        if username:
            try:
                user = CustomUser.objects.get(username=username)
                return Response({'exists': True}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({'exists': False}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Username not provided'}, status=status.HTTP_400_BAD_REQUEST)
