import json
from django.db import transaction
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from permissions.response import CustomResponseMixin
from students.models import DeletedStudent, StudentPayment, StudentCharity, StudentHistoryGroups, DeletedNewStudent, \
    Student
from students.serializers import DeletedStudentSerializer, StudentPaymentSerializer, StudentCharitySerializer, \
    StudentHistoryGroupsSerializer, StudentSerializer, StudentListSerializer
from attendances.models import AttendancePerMonth


class StudentCreateView(CustomResponseMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentUpdateView(CustomResponseMixin, generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        other_serializer = StudentListSerializer(instance)
        return Response(other_serializer.data, status=status.HTTP_200_OK)


class StudentDestroyView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            student = self.get_object()
            new_student, created = DeletedNewStudent.objects.get_or_create(student=student)
            if not created:
                new_student.delete()
                return Response({"msg": "O'quvchi muvofaqqiyatlik qaytarildi !"}, status=status.HTTP_200_OK)
            return Response({"msg": "O'quvchi muvofaqqiyatlik o'chirildi !"}, status=status.HTTP_200_OK)


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
            attendance_per_month = get_object_or_404(AttendancePerMonth, id=student_payment.attendance.id)
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

    queryset = DeletedStudent.objects.filter(deleted=True).all()
    serializer_class = DeletedStudentSerializer


class CreateDiscountForSchool(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        required_fields = ['discount', 'student', 'reason']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return Response(
                {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        discount = data['discount']
        student_id = data['student']
        reason = data['reason']

        try:
            student = Student.objects.get(pk=student_id)
            attendances = AttendancePerMonth.objects.filter(student_id=student_id)
            attendances.update(discount=discount)

            StudentCharity.objects.update_or_create(
                student=student,
                defaults={
                    'charity_sum': discount,
                    'name': reason,
                    "group": student.groups_student.first(),
                    "branch": student.user.branch
                }
            )
            return Response({"msg": "Chegirma muvaffaqiyatli yaratildi !"}, status=status.HTTP_200_OK)

        except Student.DoesNotExist:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

