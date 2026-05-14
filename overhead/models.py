from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from payments.models import PaymentTypes


class OverheadType(models.Model):
    name = models.CharField(null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    cost = models.IntegerField(null=True, blank=True)
    changeable = models.BooleanField(default=True)
    branch = models.ForeignKey('branch.Branch', on_delete=models.SET_NULL, null=True, blank=True, related_name='overhead_types')
    management_id = models.IntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)


class OverheadTypeLog(models.Model):
    overhead_type = models.ForeignKey(OverheadType, on_delete=models.CASCADE, related_name='logs')
    cost = models.IntegerField(null=True)
    is_paid = models.BooleanField(default=False)
    is_prepaid = models.BooleanField(default=False)
    paid_date = models.DateTimeField(null=True, blank=True)
    overhead = models.ForeignKey('Overhead', on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey('branch.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    @property
    def paid_amount(self) -> int:
        return sum(p.amount for p in self.payments.all() if not p.deleted)

    @property
    def remaining_amount(self) -> int:
        return max(0, (self.cost or 0) - self.paid_amount)

    @property
    def payment_status(self) -> str:
        paid = self.paid_amount
        if paid <= 0:
            return "unpaid"
        if paid < (self.cost or 0):
            return "partial"
        return "paid"

    def convert_json(self):
        payments = [p for p in self.payments.all() if not p.deleted]
        return {
            "id": self.id,
            "overhead_type_id": self.overhead_type_id,
            "overhead_type_name": self.overhead_type.name,
            "cost": self.cost,
            "is_paid": self.is_paid,
            "is_prepaid": self.is_prepaid,
            "paid_date": self.paid_date.strftime("%d.%m.%Y") if self.paid_date else None,
            "overhead_id": self.overhead_id,
            "branch_id": self.branch_id,
            "date": self.date.strftime("%d.%m.%Y") if self.date else None,
            "paid_amount": self.paid_amount,
            "remaining_amount": self.remaining_amount,
            "payment_status": self.payment_status,
            "payments": [p.convert_json() for p in payments],
        }


class OverheadTypeLogPayment(models.Model):
    overhead_type_log = models.ForeignKey(
        OverheadTypeLog, on_delete=models.CASCADE, related_name='payments',
    )
    payment_type = models.ForeignKey(
        PaymentTypes, on_delete=models.SET_NULL, null=True, blank=True,
    )
    overhead = models.ForeignKey(
        'Overhead', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='split_payments',
    )
    amount = models.IntegerField()
    paid_date = models.DateTimeField()
    note = models.CharField(max_length=500, null=True, blank=True)
    created_by = models.ForeignKey(
        'user.CustomUser', on_delete=models.SET_NULL, null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    management_id = models.IntegerField(null=True, blank=True, unique=True)

    def convert_json(self):
        return {
            "id": self.id,
            "overhead_type_log_id": self.overhead_type_log_id,
            "payment_type_id": self.payment_type_id,
            "payment_type_name": self.payment_type.name if self.payment_type_id else None,
            "overhead_id": self.overhead_id,
            "amount": self.amount,
            "paid_date": self.paid_date.strftime("%d.%m.%Y") if self.paid_date else None,
            "note": self.note,
        }


@receiver(post_migrate)
def create_default_overhead_types(sender, **kwargs):
    default_values = [
        ("Gaz", 1),
        ("Svet", 2),
        ("Suv", 3),
        ("Arenda", 4),
        ("Oshxona uchun", 5),
        ("Reklama uchun", 6),
        ("Boshqa", 7)
    ]
    for value, order in default_values:
        exists = OverheadType.objects.filter(name=value).exists()
        if not exists:
            OverheadType.objects.create(name=value, order=order)
        else:
            OverheadType.objects.filter(name=value).update(order=order)
    # default_values = ["Gaz", "Svet", "Suv", "Arenda", "Oshxona uchun", "Reklama uchun", "Boshqa"]
    # for value in default_values:
    #     OverheadType.objects.get_or_create(name=value)


class Overhead(models.Model):
    name = models.CharField(max_length=300, null=True, blank=True)
    payment = models.ForeignKey(PaymentTypes, on_delete=models.CASCADE, related_name='payment_type_id')
    created = models.DateField(auto_now_add=False)
    price = models.IntegerField(null=True)
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, null=True)
    type = models.ForeignKey(OverheadType, on_delete=models.SET_NULL, null=True)
    # old_id = models.IntegerField(null=True, unique=True)
    deleted = models.BooleanField(default=False)

