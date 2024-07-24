from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

from branch.models import Branch
from payments.models import PaymentTypes
from language.models import Language
from django.conf import settings


class CustomAutoGroup(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='custom_permission')
    salary = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.group.name} - Salary: {self.salary}"


class CustomUser(AbstractUser):
    name = models.CharField(max_length=200, blank=True, null=True)
    surname = models.CharField(max_length=200, blank=True, null=True)
    username = models.CharField(max_length=200, blank=True, null=True, unique=True)
    father_name = models.CharField(max_length=200, blank=True, null=True)
    profile_img = models.ImageField(
        null=True, blank=True, upload_to='profiles/', default="")
    birth_date = models.DateTimeField(null=True)
    registered_date = models.DateTimeField(auto_now_add=True, )
    phone = models.CharField(max_length=200, blank=True, null=True)
    age = models.CharField(max_length=200, blank=True, null=True)
    comment = models.CharField(max_length=200, blank=True, null=True)
    observer = models.BooleanField(default=False, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True)
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # related_name'ni o'zgartiring
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',  # related_name'ni o'zgartiring
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='custom_user',
    )

    # acces models.ManyToManyField(Student)

    class Meta:
        ordering = ['id']

    @property
    def imageURL(self):
        try:
            url = self.profile_img.url
        except:
            url = ''
        return url


class UserSalary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    permission = models.ForeignKey(CustomAutoGroup, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    total_salary = models.IntegerField(blank=True, null=True)
    taken_salary = models.IntegerField(blank=True, null=True)
    remaining_salary = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['id']


class UserSalaryList(models.Model):
    user_salary = models.ForeignKey(UserSalary, on_delete=models.SET_NULL, null=True)
    permission = models.ForeignKey(CustomAutoGroup, on_delete=models.SET_NULL, null=True)
    payment_types = models.ForeignKey(PaymentTypes, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    salary = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(null=False)
    comment = models.CharField(max_length=100, blank=True, null=True)
    deleted = models.BooleanField(default=False, null=True)

    class Meta:
        ordering = ['id']
