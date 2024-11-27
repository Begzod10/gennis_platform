from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone


class FrontedPageType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


@receiver(post_migrate)
def create_fronted_types(sender, **kwargs):
    default_values = [{"name": "gallery"}, {"name": "programs"}, {"name": "student_profile"}, {"name": "news"},
                      {"name": "vission_missoin"}, {"name": "extra_curricular"}, {"name": "curricular"},
                      {"name": "intro"}, {"name": "certificates"}]
    for value in default_values:
        FrontedPageType.objects.get_or_create(**value)


class FrontedPage(models.Model):
    name = models.CharField(max_length=100,null=True)
    type = models.ForeignKey(FrontedPageType, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True)
    date = models.DateField(null=True, default=timezone.now)

    def __str__(self):
        return self.name


class FrontedPageImage(models.Model):
    page = models.ForeignKey(FrontedPage, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(null=True, blank=True, upload_to='fronted_pages/')
