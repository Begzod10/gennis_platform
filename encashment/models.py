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
