from rest_framework import serializers

from attendances.models import AttendancePerMonth
from branch.models import Branch
from payments.models import PaymentTypes
from students.models import (Student, StudentPayment)
from teachers.models import TeacherBlackSalary


class StudentPaymentSerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(queryset=Student.objects.all(), slug_field='old_id')
    branch = serializers.SlugRelatedField(queryset=Branch.objects.all(), slug_field='old_id')
    payment_type = serializers.SlugRelatedField(queryset=PaymentTypes.objects.all(), slug_field='old_id')
    payment_sum = serializers.IntegerField(required=False)
    status = serializers.BooleanField(required=False)

    class Meta:
        model = StudentPayment
        fields = ['id', 'student', 'payment_type', 'payment_sum', 'status', 'branch']

    def create(self, validated_data):
        print(validated_data)
        attendance_per_months = AttendancePerMonth.objects.get(student=validated_data.get('student'),
                                                               status=False).all()
        student = Student.objects.get(pk=validated_data.get('student'))
        student_payment = StudentPayment.objects.create(**validated_data)
        payment_sum = student_payment.payment_sum + student_payment.extra_payment
        for attendance_per_month in attendance_per_months:
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
        attendance_per_months = AttendancePerMonth.objects.filter(student=validated_data.get('student'),
                                                                  status=False).all()
        for attendance_per_month in attendance_per_months:
            total_debt += attendance_per_month.total_debt
            remaining_debt += attendance_per_month.remaining_debt
        if remaining_debt == 0:
            student.debt_status = 0
        elif student.total_payment_month > total_debt:
            student.debt_status = 1
            TeacherBlackSalary.objects.filter(student=student, status=False).update(status=True)
        elif student.total_payment_month < total_debt:
            student.debt_status = 2
        student.save()
        return student_payment

    def delete(self, instance):
        instance.deleted = True
        instance.save()
        instance.student.extra_payment -= instance.payment_sum
        instance.student.extra_payment.save()
        return instance
