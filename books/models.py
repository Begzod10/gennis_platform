from django.db import models
from django.conf import settings
from students.models import Student
from teachers.models import Teacher
from group.models import Group
from branch.models import Branch
from payments.models import PaymentTypes


class Book(models.Model):
    name = models.CharField(max_length=250)
    desc = models.CharField(null=True)
    price = models.IntegerField(null=False)
    own_price = models.IntegerField(null=True)
    share_price = models.IntegerField(null=True)
    file = models.FileField(upload_to='books/files', null=True)


class BookImage(models.Model):
    image = models.ImageField(upload_to='books/images', null=True)
    book = models.ForeignKey(Book, related_name='book_image_book_id', on_delete=models.CASCADE)


class CollectedBookPayments(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='collected_book_payment_branch')
    payment_type = models.ForeignKey(PaymentTypes, on_delete=models.CASCADE,
                                     related_name='collected_book_payment_payment_type')
    total_debt = models.IntegerField(null=True)
    month_date = models.DateTimeField(null=True)
    created_date = models.DateTimeField(null=True)
    received_date = models.DateTimeField(null=True)
    status = models.BooleanField(null=True, default=False)


class BookOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book_order_user',
                             null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='book_order_student', null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='book_order_teacher', null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='book_order_group', null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_order_book')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='book_order_branch')
    collected_payment = models.ForeignKey(CollectedBookPayments, on_delete=models.CASCADE,
                                          related_name='book_order_collected_payment')
    count = models.IntegerField(null=True)
    admin_status = models.BooleanField(null=True, default=False)
    editor_status = models.BooleanField(null=True, default=False)
    deleted = models.BooleanField(default=False)
    reason = models.CharField(max_length=250)
    day = models.DateTimeField(null=True)


class CenterBalance(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='center_balance_branch')
    total_money = models.IntegerField(null=True)
    remaining_money = models.IntegerField(null=True)
    taken_money = models.IntegerField(null=True)
    month_date = models.DateTimeField(null=True)


class CenterOrders(models.Model):
    balance = models.ForeignKey(CenterBalance, on_delete=models.CASCADE, related_name='center_orders_center_balance')
    order = models.ForeignKey(BookOrder, on_delete=models.CASCADE, related_name='center_balance_book_order')


class BalanceOverhead(models.Model):
    balance = models.ForeignKey(CenterBalance, on_delete=models.CASCADE, related_name='balance_overhead_center_balance')
    payment_type = models.ForeignKey(PaymentTypes, on_delete=models.CASCADE,
                                     related_name='balance_overhead_payment_type')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='balance_overhead_branch')
    overhead_sum = models.IntegerField(null=True)
    reason = models.CharField(max_length=250, null=True)
    deleted = models.BooleanField(default=False)
    day = models.DateTimeField(null=True)
