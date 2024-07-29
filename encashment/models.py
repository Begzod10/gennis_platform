from django.db import models


class Encashment(models.Model):
    ot = models.DateField()
    do = models.DateField()
    payment_type = models.ForeignKey('payments.PaymentTypes', on_delete=models.CASCADE)
    total_teacher_salary = models.BigIntegerField()
    total_student_salary = models.BigIntegerField()
    total_staff_salary = models.BigIntegerField()
    total_branch_payment = models.BigIntegerField()
    total_overhead = models.BigIntegerField()
