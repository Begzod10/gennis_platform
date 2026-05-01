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


class BranchLoan(models.Model):
    DIRECTION_CHOICES = [
        ('out', 'Branch lent'),
        ('in', 'Branch borrowed'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('settled', 'Settled'),
        ('cancelled', 'Cancelled'),
    ]

    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.PROTECT,
        related_name='loans',
    )

    counterparty = models.ForeignKey(
        'user.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='loans',
    )
    counterparty_name = models.CharField(max_length=200, null=True, blank=True)
    counterparty_surname = models.CharField(max_length=200, null=True, blank=True)
    counterparty_phone = models.CharField(max_length=50, null=True, blank=True)

    direction = models.CharField(max_length=8, choices=DIRECTION_CHOICES)
    principal_amount = models.BigIntegerField()

    issued_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)

    reason = models.CharField(max_length=500, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='active')
    settled_date = models.DateField(null=True, blank=True)
    cancelled_reason = models.CharField(max_length=500, null=True, blank=True)

    created_by = models.ForeignKey(
        'user.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_loans',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    management_id = models.BigIntegerField(null=True, blank=True, unique=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']

    def paid_total(self):
        from django.db.models import Sum
        opposite_is_give = (self.direction == 'in')
        agg = self.transactions.filter(deleted=False, is_give=opposite_is_give).aggregate(
            total=Sum('amount'),
        )
        return agg['total'] or 0

    def remaining_amount(self):
        return max(0, self.principal_amount - self.paid_total())

    def is_settled(self):
        return self.paid_total() >= self.principal_amount

    def recompute_status(self, save=True):
        if self.status == 'cancelled':
            return
        if self.is_settled():
            self.status = 'settled'
            if not self.settled_date:
                from django.utils import timezone
                self.settled_date = timezone.localdate()
        else:
            self.status = 'active'
            self.settled_date = None
        if save:
            self.save(update_fields=['status', 'settled_date', 'updated_at'])

    def counterparty_payload(self):
        if self.counterparty_id:
            return {
                'id': self.counterparty_id,
                'name': self.counterparty.name if self.counterparty else None,
                'surname': self.counterparty.surname if self.counterparty else None,
                'phone': self.counterparty.phone if self.counterparty else None,
            }
        return {
            'id': None,
            'name': self.counterparty_name,
            'surname': self.counterparty_surname,
            'phone': self.counterparty_phone,
        }

    def convert_json(self, with_transactions=False):
        principal = int(self.principal_amount or 0)
        paid = int(self.paid_total() or 0)
        data = {
            'id': self.id,
            'branch_id': self.branch_id,
            'counterparty': self.counterparty_payload(),
            'direction': self.direction,
            'principal_amount': principal,
            'paid_total': paid,
            'remaining_amount': max(0, principal - paid),
            'is_settled': paid >= principal,
            'issued_date': self.issued_date.strftime('%Y-%m-%d') if self.issued_date else None,
            'due_date': self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            'settled_date': self.settled_date.strftime('%Y-%m-%d') if self.settled_date else None,
            'reason': self.reason,
            'notes': self.notes,
            'status': self.status,
            'cancelled_reason': self.cancelled_reason,
            'management_id': self.management_id,
        }
        if with_transactions:
            data['transactions'] = [tx.convert_json() for tx in self.transactions.filter(deleted=False).order_by('date', 'id')]
        return data


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

    loan = models.ForeignKey(
        BranchLoan,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='transactions',
    )

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
            'loan_id': self.loan_id,
        }
