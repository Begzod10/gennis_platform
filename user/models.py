from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    name = models.CharField(max_length=200, blank=True, null=True)
    surname = models.CharField(max_length=200, blank=True, null=True)
    username = models.CharField(max_length=200, blank=True, null=True,unique=True)
    father_name = models.CharField(max_length=200, blank=True, null=True)
    profile_img = models.ImageField(
        null=True, blank=True, upload_to='profiles/', default="")
    birth_date = models.DateTimeField()
    registered_date = models.DateTimeField(default=timezone.now)
    phone = models.CharField(max_length=200, blank=True, null=True)
    age = models.CharField(max_length=200, blank=True, null=True)
    comment = models.CharField(max_length=200, blank=True, null=True)
    observer = models.BooleanField(default=False, null=True)
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

    def __str__(self):
        return str(self.username)

    class Meta:
        ordering = ['id']

    @property
    def imageURL(self):
        try:
            url = self.profile_img.url
        except:
            url = ''
        return url
