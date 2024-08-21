from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)
    ball_number = models.IntegerField(default=0)
    classroom_id = models.IntegerField()
    disabled = models.BooleanField(default=False)
    old_id = models.IntegerField(null=True, unique=True)


    def __str__(self):
        return self.name


class SubjectLevel(models.Model):
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='levels')
    classroom_id = models.IntegerField()
    disabled = models.BooleanField(default=False)
    old_id = models.IntegerField(null=True, unique=True)

