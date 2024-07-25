from django.db import models


class PaymentTypes(models.Model):
    name = models.CharField(null=False, blank=False, max_length=250)

    def __str__(self):
        return self.name


class PaymentTypes2(models.Model):
    name = models.CharField(null=False, blank=False, max_length=250)

    def __str__(self):
        return self.name