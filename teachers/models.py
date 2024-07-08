from django.db import models
from django.conf import settings
from subjects.models import Subject

<<<<<<< HEAD
=======
from user.serializers import UserSerializer, CustomUser

>>>>>>> 55b1efb65c1279aeaf68712f2b77d013d9849438

class Teacher(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_user')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)
    color = models.CharField(max_length=50)
    total_students = models.IntegerField()
<<<<<<< HEAD
=======

# class TeacherSalary()
>>>>>>> 55b1efb65c1279aeaf68712f2b77d013d9849438
