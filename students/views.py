from rest_framework import generics, status
from rest_framework.response import Response
from .models import Student, StudentPayment, DeletedStudent, StudentHistoryGroups
from .serializers import (StudentCharitySerializer, StudentCharity)
from .serializers import (StudentSerializer, StudentHistoryGroupsSerializer, StudentPaymentSerializer,
                          DeletedStudentSerializer)
from rest_framework.views import APIView


class StudentListCreateView(APIView):
    def get(self, request, *args, **kwargs):
        deleted_student_ids = DeletedStudent.objects.values_list('student_id', flat=True)
        active_students = Student.objects.exclude(id__in=deleted_student_ids)
        student_serializer = StudentSerializer(active_students, many=True)

        deleted_students = DeletedStudent.objects.all()
        deleted_student_serializer = DeletedStudentSerializer(deleted_students, many=True)
        data = {
            'active_students': student_serializer.data,
            'deleted_students': deleted_student_serializer.data,
        }

        return Response(data)

    def post(self, request, *args, **kwargs):
        student_serializer = StudentSerializer(data=request.data)
        if student_serializer.is_valid():
            student_serializer.save()
            return Response(student_serializer.data, status=201)
        return Response(student_serializer.errors, status=400)


class StudentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        create = DeletedStudent.objects.create(student=student)
        return Response({"detail": "Student was deleted successfully"}, status=status.HTTP_200_OK)


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


class DeletedStudentDestroy(generics.DestroyAPIView):
    queryset = DeletedStudent.objects.all()
    serializer_class = DeletedStudentSerializer
