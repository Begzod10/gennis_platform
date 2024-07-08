from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema

from .serializers import (StudentSerializer, Student, StudentHistoryGroupsSerializer, StudentHistoryGroups,
                          StudentCharitySerializer, StudentCharity)


class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi


class StudentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi


class StudentHistoryGroupsListCreateView(generics.ListCreateAPIView):
    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi
    #


class StudentHistoryGroupsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsSerializer
    # permission_classes = (
    #     IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)  # login qilgan yoki yuq ligini va admin emasligini tekshiradi


class StudentCharityListCreate(generics.ListCreateAPIView):
    serializer_class = StudentCharitySerializer

    def get_queryset(self):
        student_id = self.request.query_params.get('student_id', None)
        if student_id is not None:
            return StudentCharity.objects.filter(student_id=student_id)
        return StudentCharity.objects.all()


class StudentCharityRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentCharity.objects.all()
    serializer_class = StudentCharitySerializer
