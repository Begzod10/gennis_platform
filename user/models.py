from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User, Group, Permission
from django.db import models

from branch.models import Branch
from language.models import Language
from payments.models import PaymentTypes


class CustomAutoGroup(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='custom_permission')
    salary = models.IntegerField(blank=True, null=True, default=0)
    old_id = models.IntegerField(blank=True, null=True, unique=True)
    user = models.ForeignKey('user.CustomUser', blank=True, null=True, on_delete=models.CASCADE)
    deleted = models.BooleanField(default=False, null=True)
    share = models.IntegerField(default=0, null=True)

    def __str__(self):
        return f"{self.group.name} - Salary: {self.salary}"


class CustomUser(AbstractUser):
    LEVEL_CHOICES = (
        (1, "1-daraja"),
        (2, "2-daraja"),
        (3, "3-daraja"),
        (4, "4-daraja"),
    )

    name = models.CharField(max_length=200, blank=True, null=True)
    surname = models.CharField(max_length=200, blank=True, null=True)
    username = models.CharField(max_length=200, blank=True, null=True, unique=True)
    father_name = models.CharField(max_length=200, blank=True, null=True)
    profile_img = models.ImageField(
        null=True, blank=True, upload_to='profiles/', default="")
    birth_date = models.DateField(null=True)
    registered_date = models.DateField(auto_now_add=True, )
    phone = models.CharField(max_length=200, blank=True, null=True)
    comment = models.CharField(max_length=200, blank=True, null=True)
    observer = models.BooleanField(default=False, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)
    old_id = models.IntegerField(null=True, unique=True)
    uuid = models.CharField(max_length=200, blank=True, null=True)
    balance = models.CharField(null=True)
    # test_text = models.CharField(null=True, blank=True)
    # turon_old_id = models.IntegerField(null=True, unique=True)

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
    file = models.FileField(upload_to='documents/', null=True, blank=True, default="")

    face_id = models.CharField(max_length=200, blank=True, null=True)

    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=4)

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

    def calculate_age(self):
        if not self.birth_date:
            return None
        today = datetime.today()
        age = today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return age


class UserSalary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    permission = models.ForeignKey(CustomAutoGroup, on_delete=models.SET_NULL, null=True)
    date = models.DateField(auto_now_add=False, null=True, blank=True)
    total_salary = models.IntegerField(blank=True, null=True)
    taken_salary = models.IntegerField(blank=True, null=True)
    remaining_salary = models.IntegerField(blank=True, null=True)
    old_id = models.IntegerField(blank=True, null=True, unique=True)

    class Meta:
        ordering = ['-date']


class UserSalaryList(models.Model):
    user_salary = models.ForeignKey(UserSalary, on_delete=models.SET_NULL, null=True)
    permission = models.ForeignKey(CustomAutoGroup, on_delete=models.SET_NULL, null=True)
    payment_types = models.ForeignKey(PaymentTypes, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    salary = models.IntegerField(blank=True, null=True)
    date = models.DateField(null=True, auto_now_add=False)
    comment = models.CharField(max_length=100, blank=True, null=True)
    deleted = models.BooleanField(default=False, null=True)
    old_id = models.IntegerField(null=True, blank=True, unique=True)

    class Meta:
        ordering = ['-date']
