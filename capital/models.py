from django.db import models
from branch.models import Branch
from payments.models import PaymentTypes


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
    added_date = models.DateTimeField(auto_now_add=True)
    term = models.DateTimeField()
    curriculum_hours = models.IntegerField()
    img = models.ImageField(upload_to='capital/images', null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    payment_type = models.ForeignKey(PaymentTypes, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(CapitalCategory, on_delete=models.SET_NULL, null=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']


class CapitalTerm(models.Model):
    down_cost = models.IntegerField()
    month_date = models.DateTimeField()
    capital = models.ForeignKey(Capital, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['id']
