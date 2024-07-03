from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import generics

from .serializers import *


# def loginUser(request):
#     if request.method == 'POST':
#         username = request.POST['username'].lower()
#         password = request.POST['password']
#
#         user = authenticate(request, username=username, password=password)
#         print(user)
#         if user is not None:
#             return True
#         else:
#             return False
#     return render(request, '')



class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
