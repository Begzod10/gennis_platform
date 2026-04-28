from django.core.validators import FileExtensionValidator
from django.db import models


class Vacancy(models.Model):
    name = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=255, null=True)
    letter = models.CharField(max_length=255, null=True)
    cv = models.FileField(
        upload_to='vacancy/files',
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])
        ]
    )
    date = models.DateField(null=True,auto_now_add=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    name = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True)
    message = models.TextField(null=True)
    organization = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    enquiry_type = models.CharField(max_length=255, null=True)
    date = models.DateField(null=True,auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

class News(models.Model):
    title = models.CharField(max_length=255, null=True)
    date = models.DateField(null=True)
    content = models.TextField(null=True)
    image = models.ImageField()

