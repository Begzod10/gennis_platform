from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from attendances.models import AttendancePerMonth
from attendances.serializers import AttendancePerMonthSerializer


# Create your views here.


class DeleteAttendanceMonthApiView(generics.DestroyAPIView):
    queryset = AttendancePerMonth.objects.all()
    serializer_class = AttendancePerMonthSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"msg": "O'chirildi"}, status=status.HTTP_200_OK)
