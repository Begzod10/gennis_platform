from django.db import models


class Term(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()


class Test(models.Model):
    name = models.CharField(max_length=255)
    weight = models.IntegerField()
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE)
    group = models.ForeignKey('group.Group', on_delete=models.CASCADE)
    class_number = models.ForeignKey('classes.ClassNumber', on_delete=models.CASCADE)



class Assignment(models.Model):
    percentage = models.IntegerField()
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
