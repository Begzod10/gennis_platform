from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver


class Hours(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    name = models.CharField()
    order = models.IntegerField()
    types = models.ManyToManyField('HoursType', related_name='hours')


class HoursType(models.Model):
    name = models.CharField()


@receiver(post_migrate)
def create_default_overhead_types(sender, **kwargs):
    default_values = [{'name': 'Initial'},
                      {'name': 'High'}]
    for value in default_values:
       HoursType.objects.get_or_create(name=value['name'])



class ClassTimeTable(models.Model):
    group = models.ForeignKey('group.Group', on_delete=models.CASCADE, null=True)
    week = models.ForeignKey('time_table.WeekDays', on_delete=models.CASCADE, null=True)
    room = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, null=True)
    hours = models.ForeignKey(Hours, on_delete=models.CASCADE)
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE)
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, null=True)
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, null=True)
    flow = models.ForeignKey('flows.Flow', on_delete=models.CASCADE, null=True)
    name = models.CharField()
    students = models.ManyToManyField('students.Student', related_name='class_time_table')
    date = models.DateField(null=True)
