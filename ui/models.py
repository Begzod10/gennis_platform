from django.db import models
from django.utils import timezone


class FrontedPageType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FrontedPage(models.Model):
    name = models.CharField(max_length=100)
    type = models.ForeignKey(FrontedPageType, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True)
    date = models.DateField(null=True, default=timezone.now)

    def __str__(self):
        return self.name


class FrontedPageImage(models.Model):
    page = models.ForeignKey(FrontedPage, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(null=True, blank=True, upload_to='fronted_pages/')
