from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from payments.models import PaymentTypes


class OverheadType(models.Model):
    name = models.CharField(null=True, blank=True)


@receiver(post_migrate)
def create_default_overhead_types(sender, **kwargs):
    default_values = ["Gaz", "Svet", "Suv", "Arenda", "Boshqa"]
    for value in default_values:
        OverheadType.objects.get_or_create(name=value)


class Overhead(models.Model):
    name = models.CharField(max_length=300, null=True,blank=True)
    payment = models.ForeignKey(PaymentTypes, on_delete=models.CASCADE, related_name='payment_type_id')
    created = models.DateField(auto_now_add=False)
    price = models.IntegerField(null=True)
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, null=True)
    type = models.ForeignKey(OverheadType, on_delete=models.SET_NULL, null=True)
    old_id = models.IntegerField(null=True, unique=True)
    deleted = models.BooleanField(default=False)
