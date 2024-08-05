from django.db import models


class PaymentTypes(models.Model):
    name = models.CharField(null=False, blank=False, max_length=250)
    old_id = models.IntegerField(null=True, unique=True)

    def __str__(self):
        return self.name
