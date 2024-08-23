from django.db import models
from payments.models import PaymentTypes


class Overhead(models.Model):
    name = models.CharField(max_length=300, null=True)
    payment = models.ForeignKey(PaymentTypes, on_delete=models.CASCADE, related_name='payment_type_id')
    created = models.DateTimeField(auto_now_add=False)
    price = models.IntegerField(null=True)
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, null=True)
    old_id = models.IntegerField(null=True, unique=True)
