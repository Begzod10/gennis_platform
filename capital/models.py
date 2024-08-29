from django.db import models
from branch.models import Branch
from payments.models import PaymentTypes
from django.conf import settings


class CapitalCategory(models.Model):
    name = models.CharField(max_length=100)
    img = models.ImageField(upload_to='capital_category/images', null=True)
    id_number = models.CharField(max_length=100)

    class Meta:
        ordering = ['id']


class Capital(models.Model):
    name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=100)
    price = models.IntegerField()
    total_down_cost = models.IntegerField()
    added_date = models.DateField(auto_now_add=True)
    term = models.BigIntegerField()
    curriculum_hours = models.IntegerField()
    img = models.ImageField(upload_to='capital/images', null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='capital_branch')
    payment_type = models.ForeignKey(PaymentTypes, on_delete=models.SET_NULL, null=True,
                                     related_name='capital_payment_type')
    category = models.ForeignKey(CapitalCategory, on_delete=models.SET_NULL, null=True, related_name='capital_category')
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']


class CapitalTerm(models.Model):
    down_cost = models.IntegerField()
    month_date = models.DateField(auto_now_add=True)
    capital = models.ForeignKey(Capital, on_delete=models.SET_NULL, null=True, related_name='capital_term_capital')

    class Meta:
        ordering = ['id']


class OldCapital(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    by_who = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='old_capital_user',
                               null=True)
    added_date = models.DateField(auto_now_add=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='old_capital_branch')
    payment_type = models.ForeignKey(PaymentTypes, on_delete=models.SET_NULL, null=True,
                                     related_name='old_capital_payment_type')
    old_id = models.IntegerField(null=True, unique=True)
    deleted = models.BooleanField(default=False)


    class Meta:
        ordering = ['id']
