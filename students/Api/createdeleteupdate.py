from rest_framework import generics
from students.serializers import DeletedStudentSerializer, StudentPaymentSerializer, StudentCharitySerializer, \
    StudentHistoryGroupsSerializer, StudentSerializer
from students.models import DeletedStudent, StudentPayment, StudentCharity, StudentHistoryGroups, DeletedNewStudent, \
    Student
from rest_framework.response import Response
from rest_framework import status


class StudentCreateView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentUpdateView(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentDestroyView(generics.DestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        DeletedNewStudent.objects.create(student=student)  # new studentni ochirish
        return Response({"detail": "Student was deleted successfully"}, status=status.HTTP_200_OK)


class StudentHistoryGroupsCreateView(generics.CreateAPIView):
    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsSerializer


class StudentHistoryGroupsUpdateView(generics.UpdateAPIView):
    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsSerializer


class StudentHistoryGroupsDestroyView(generics.DestroyAPIView):
    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsSerializer


class StudentCharityCreateView(generics.CreateAPIView):
    queryset = StudentCharity.objects.all()
    serializer_class = StudentCharitySerializer


class StudentCharityUpdateView(generics.UpdateAPIView):
    queryset = StudentCharity.objects.all()
    serializer_class = StudentCharitySerializer


class StudentCharityDestroyView(generics.DestroyAPIView):
    queryset = StudentCharity.objects.all()
    serializer_class = StudentCharitySerializer


class StudentPaymentCreateView(generics.CreateAPIView):
    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentSerializer


class StudentPaymentUpdateView(generics.UpdateAPIView):
    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentSerializer


class StudentPaymentDestroyView(generics.DestroyAPIView):
    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted = True
        instance.save()
        student = instance.student
        if not instance.payment_sum:
            instance.payment_sum = 0
        if student.extra_payment:
            extra_payment = float(student.extra_payment)
            student.extra_payment = extra_payment - instance.payment_sum
            student.save()
        return Response({'message': 'Payment record successfully deleted.'}, status=status.HTTP_200_OK)


class DeletedStudentDestroy(generics.DestroyAPIView):
    queryset = DeletedStudent.objects.all()
    serializer_class = DeletedStudentSerializer
