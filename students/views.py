from rest_framework import generics

from group.models import StudentHistoryGroups
from .models import Student, StudentPayment
from .serializers import (StudentCharitySerializer, StudentCharity)
from .serializers import (StudentSerializer, StudentHistoryGroupsSerializer, StudentPaymentSerializer)


class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentHistoryGroupsListCreateView(generics.ListCreateAPIView):
    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsSerializer


class StudentHistoryGroupsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsSerializer


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


class StudentPaymentListCreateView(generics.ListCreateAPIView):
    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentSerializer


class StudentPaymentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentSerializer
