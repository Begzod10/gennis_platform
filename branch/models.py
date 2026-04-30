from django.db import models

from location.models import Location


class Branch(models.Model):
    name = models.CharField(max_length=255)
    number = models.CharField(null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, null=True)
    location_text = models.CharField(max_length=255, null=True)
    map_link = models.CharField(null=True, blank=True)
    code = models.IntegerField(null=True)
    phone_number = models.CharField(max_length=20, null=True)
    director_fio = models.CharField(max_length=255, null=True)
    location_type = models.CharField(max_length=255, null=True)
    district = models.CharField(max_length=255, null=True)
    bank_sheet = models.CharField(null=True)
    inn = models.CharField(max_length=255, null=True)
    bank = models.CharField(max_length=255, null=True)
    mfo = models.CharField(max_length=50, null=True)
    campus_name = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    year = models.DateField(null=True)
    old_id = models.IntegerField(unique=True, null=True)

    def __str__(self):
        return self.name


class BranchTransaction(models.Model):
    amount = models.BigIntegerField()
    is_give = models.BooleanField()
    reason = models.CharField(max_length=500, null=True, blank=True)

    person = models.ForeignKey(
        'user.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='branch_transactions',
    )
    person_name = models.CharField(max_length=200, null=True, blank=True)
    person_surname = models.CharField(max_length=200, null=True, blank=True)
    person_phone = models.CharField(max_length=50, null=True, blank=True)

    payment_type = models.ForeignKey(
        'payments.PaymentTypes',
        on_delete=models.PROTECT,
        related_name='branch_transactions',
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name='branch_transactions',
    )
    date = models.DateField()

    created_by = models.ForeignKey(
        'user.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_branch_transactions',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']

    def convert_json(self):
        if self.person_id:
            person = {
                'id': self.person_id,
                'name': self.person.name if self.person else None,
                'surname': self.person.surname if self.person else None,
                'phone': self.person.phone if self.person else None,
            }
        else:
            person = {
                'id': None,
                'name': self.person_name,
                'surname': self.person_surname,
                'phone': self.person_phone,
            }
        return {
            'id': self.id,
            'amount': self.amount,
            'is_give': self.is_give,
            'direction': 'give' if self.is_give else 'receive',
            'reason': self.reason,
            'person': person,
            'payment_type': {
                'id': self.payment_type_id,
                'name': self.payment_type.name if self.payment_type else None,
            },
            'branch_id': self.branch_id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
        }
