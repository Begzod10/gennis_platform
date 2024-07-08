from django.db import models

from group.models import Student, Teacher, Group


class AttendancePerMonth(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True,
                                related_name='attendance_per_month_teacher_id')
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True,
                                related_name='attendance_per_month_student_id')
    date = models.DateField(auto_now_add=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name='attendance_per_month_group_id')
    status = models.IntegerField()
    total_debt = models.IntegerField()
    total_salary = models.IntegerField()
    ball_percentage = models.IntegerField()
    month_date = models.DateField()
    total_charity = models.IntegerField()
    remaining_debt = models.BigIntegerField()
    payment = models.BigIntegerField()
    remaining_salary = models.BigIntegerField()
    taken_salary = models.BigIntegerField()


class AttendancePerDay(models.Model):
    per_month_id = models.ForeignKey(AttendancePerMonth, on_delete=models.SET_NULL, null=True,
                                     related_name='attendance_per_day_month_id')
    debt_per_day = models.IntegerField()
    salary_per_day = models.IntegerField()
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True,
                                related_name='attendance_per_day_student_id')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True,
                                related_name='attendance_per_day_teacher_id')
    charity_per_day = models.IntegerField()
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name='attendance_per_day_group_id')
    day_date = models.DateField()
    homework_ball = models.IntegerField()
    dictionary_ball = models.IntegerField()
    activness_ball = models.IntegerField()
    average = models.IntegerField()
    status = models.IntegerField()
