from attendances.models import AttendancePerMonth
from payments.models import PaymentTypes
from students.models import (StudentPayment)
from teachers.models import TeacherBlackSalary
from students.models import Student
from branch.models import Branch
from rest_framework import serializers


class OldIdRelatedField(serializers.RelatedField):
    def to_internal_value(self, data):
        if isinstance(data, dict):
            old_id = data.get('old_id')
            if old_id is None:
                raise serializers.ValidationError("old_id is required.")
            try:
                return self.get_queryset().get(old_id=old_id)
            except self.get_queryset().model.DoesNotExist:
                raise serializers.ValidationError(f"Object with old_id {old_id} does not exist.")
        raise serializers.ValidationError("Expected a dictionary with an 'old_id'.")

    def to_representation(self, value):
        return {
            'old_id': value.old_id,
        }


class StudentPaymentSerializerTransfer(serializers.ModelSerializer):
    student = OldIdRelatedField(queryset=Student.objects.all(), many=False)
    branch = OldIdRelatedField(queryset=Branch.objects.all(), many=False)
    payment_type = OldIdRelatedField(queryset=PaymentTypes.objects.all(), many=False)
    payment_sum = serializers.IntegerField(required=False)
    status = serializers.BooleanField(required=False)

    class Meta:
        model = StudentPayment
        fields = ['id', 'student', 'payment_type', 'payment_sum', 'status', 'branch']

    def create(self, validated_data):
        attendance_per_months = AttendancePerMonth.objects.filter(student=validated_data.get('student'), status=False)
        student = Student.objects.get(pk=validated_data.get('student').id)
        student_payment = StudentPayment.objects.create(**validated_data)
        if student_payment.extra_payment:
            payment_sum = student_payment.payment_sum + student_payment.extra_payment
        else:
            payment_sum = 0

        for attendance_per_month in attendance_per_months:
            if not attendance_per_month.remaining_debt:
                attendance_per_month.remaining_debt = 0
                attendance_per_month.save()

            if attendance_per_month.remaining_debt >= payment_sum:
                attendance_per_month.remaining_debt -= payment_sum
                attendance_per_month.payment += payment_sum
                payment_sum = 0
                if attendance_per_month.remaining_debt == 0:
                    attendance_per_month.status = True
            else:
                payment_sum -= attendance_per_month.remaining_debt
                attendance_per_month.payment += attendance_per_month.remaining_debt
                attendance_per_month.remaining_debt = 0
                attendance_per_month.status = True
            attendance_per_month.save()

        student_payment.extra_payment = payment_sum
        student_payment.save()

        total_debt = 0
        remaining_debt = 0
        attendance_per_months = AttendancePerMonth.objects.filter(student=validated_data.get('student'), status=False)

        for attendance_per_month in attendance_per_months:
            total_debt += attendance_per_month.total_debt
            remaining_debt += attendance_per_month.remaining_debt
        if not student.total_payment_month:
            student.total_payment_month = 0
            student.save()
        if remaining_debt == 0:
            student.debt_status = 0
        elif student.total_payment_month > total_debt:
            student.debt_status = 1
            TeacherBlackSalary.objects.filter(student=student, status=False).update(status=True)
        elif student.total_payment_month < total_debt:
            student.debt_status = 2

        student.save()
        return student_payment
