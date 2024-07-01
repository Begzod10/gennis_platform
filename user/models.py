from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    surname = models.CharField(max_length=200, blank=True, null=True)
    username = models.CharField(max_length=200, blank=True, null=True)
    father_name = models.CharField(max_length=200, blank=True, null=True)
    profile_img = models.ImageField(
        null=True, blank=True, upload_to='profiles/', default="")
    birth_date = models.DateTimeField()
    registered_date = models.DateTimeField(default=timezone.now)
    phone = models.CharField(max_length=200, blank=True, null=True)
    age = models.CharField(max_length=200, blank=True, null=True)
    comment = models.CharField(max_length=200, blank=True, null=True)
    observer = models.BooleanField(default=False, null=True)

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
