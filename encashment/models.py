from django.db import models

from branch.models import Branch
from payments.models import PaymentTypes


class Encashment(models.Model):
    ot = models.DateField()
    do = models.DateField()
    payment_type = models.ForeignKey(PaymentTypes, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    total_teacher_salary = models.BigIntegerField()
    total_student_payment = models.BigIntegerField()
    total_staff_salary = models.BigIntegerField()
    total_branch_payment = models.BigIntegerField()
    total_overhead = models.BigIntegerField()
    total_capital = models.BigIntegerField()


class DailySummary(models.Model):
    date = models.DateField(auto_now_add=True)
    total_students = models.BigIntegerField()
    new_students = models.BigIntegerField()
    deleted_students = models.BigIntegerField()
    present_students = models.BigIntegerField()
    new_deleted_students = models.BigIntegerField()
    total_payments = models.BigIntegerField()
    total_payments_sum = models.BigIntegerField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
