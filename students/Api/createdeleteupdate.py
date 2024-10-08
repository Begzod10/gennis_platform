from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from permissions.response import CustomResponseMixin
from students.models import DeletedStudent, StudentPayment, StudentCharity, StudentHistoryGroups, DeletedNewStudent, \
    Student
from students.serializers import DeletedStudentSerializer, StudentPaymentSerializer, StudentCharitySerializer, \
    StudentHistoryGroupsSerializer, StudentSerializer


class StudentCreateView(CustomResponseMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentUpdateView(CustomResponseMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentDestroyView(CustomResponseMixin, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        DeletedNewStudent.objects.create(student=student)  # new studentni ochirish
        return Response({"detail": "Student was deleted successfully"}, status=status.HTTP_200_OK)


class StudentHistoryGroupsCreateView(CustomResponseMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsSerializer


class StudentHistoryGroupsUpdateView(CustomResponseMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsSerializer


class StudentHistoryGroupsDestroyView(CustomResponseMixin, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentHistoryGroups.objects.all()
    serializer_class = StudentHistoryGroupsSerializer


class StudentCharityCreateView(CustomResponseMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    app_name = 'Student uchun hayriya'
    queryset = StudentCharity.objects.all()
    serializer_class = StudentCharitySerializer


class StudentCharityUpdateView(CustomResponseMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    app_name = 'Student hayriyasi'

    queryset = StudentCharity.objects.all()
    serializer_class = StudentCharitySerializer


class StudentCharityDestroyView(CustomResponseMixin, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    app_name = 'Student hayriyasi'

    queryset = StudentCharity.objects.all()
    serializer_class = StudentCharitySerializer


class StudentPaymentCreateView(CustomResponseMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentSerializer


class StudentPaymentUpdateView(CustomResponseMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentSerializer


class StudentPaymentDestroyView(CustomResponseMixin, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = StudentPayment.objects.all()
    serializer_class = StudentPaymentSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.branch.location.system.name == 'school':
            from django.shortcuts import get_object_or_404
            from attendances.models import AttendancePerMonth
            student_payment = get_object_or_404(StudentPayment, id=instance.id)
            attendance_per_month = get_object_or_404(AttendancePerMonth,
                                                     month_date__year=student_payment.added_data.year,
                                                     month_date__month=student_payment.added_data.month,
                                                     student=student_payment.student)

            attendance_per_month.remaining_debt += student_payment.payment_sum
            attendance_per_month.payment -= student_payment.payment_sum
            student_payment.deleted = True
            student_payment.save()

            if attendance_per_month.remaining_debt != 0:
                attendance_per_month.status = False

            attendance_per_month.save()

            return Response({'msg': 'Payment record successfully deleted.'}, status=status.HTTP_200_OK)

        elif instance.branch.location.system.name == 'center':
            instance.deleted = True
            instance.save()
            student = instance.student
            if not instance.payment_sum:
                instance.payment_sum = 0
            if student.extra_payment:
                extra_payment = float(student.extra_payment)
                student.extra_payment = extra_payment - instance.payment_sum
                student.save()

        return Response({'msg': 'Payment record successfully deleted.'}, status=status.HTTP_200_OK)


class DeletedStudentDestroy(CustomResponseMixin, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = DeletedStudent.objects.all()
    serializer_class = DeletedStudentSerializer
