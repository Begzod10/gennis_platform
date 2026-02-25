from django.conf import settings
from django.db import models

from branch.models import Branch
from payments.models import PaymentTypes
from subjects.models import Subject
from system.models import System
from parents.models import Parent


class TeacherSalaryType(models.Model):
    name = models.CharField()
    salary = models.IntegerField()
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    turon_old_id = models.IntegerField(null=True, unique=True)


class Teacher(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_user')
    subject = models.ManyToManyField(Subject, blank=True)
    color = models.CharField(max_length=50, null=True)
    total_students = models.IntegerField(null=True)
    premium_rate = models.IntegerField(null=True)
    class_type = models.ForeignKey('classes.ClassTypes', on_delete=models.SET_NULL, null=True)
    teacher_salary_type = models.ForeignKey(TeacherSalaryType, on_delete=models.SET_NULL, null=True)
    old_id = models.IntegerField(unique=True, null=True)
    turon_old_id = models.IntegerField(null=True, unique=True)
    branches = models.ManyToManyField(Branch, blank=True)
    group_time_table = models.ManyToManyField('time_table.GroupTimeTable', blank=True)
    salary_percentage = models.IntegerField(default=50, null=True, blank=True)
    deleted = models.BooleanField(default=False)
    deleted_date = models.DateField(null=True)
    working_hours = models.CharField(max_length=50, null=True)
    class_salary = models.IntegerField(default=0, null=True)
    # face_id = models.CharField(null=True)
    # system = models.ForeignKey('system.System', on_delete=models.SET_NULL, null=True)


class TeacherAttendance(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True,
                                related_name='teacher_attendance_teacher')
    day = models.DateField(null=True)
    entry_time = models.DateTimeField(null=True)
    leave_time = models.DateTimeField(null=True)
    status = models.BooleanField(null=True)
    system = models.ForeignKey(System, on_delete=models.SET_NULL, null=True, related_name='teacher_attendance_system')

    class Meta:
        ordering = ['id']


class TeacherSalary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teacher_id_salary')
    month_date = models.DateField(null=True, auto_now_add=False)  # true qilish kk
    total_salary = models.BigIntegerField(blank=True, null=True, default=0)
    remaining_salary = models.BigIntegerField(blank=True, null=True, default=0)
    taken_salary = models.BigIntegerField(blank=True, null=True, default=0)
    total_black_salary = models.BigIntegerField(blank=True, null=True, default=0)
    percentage = models.IntegerField(default=50)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='branch_id_salary')
    teacher_salary_type = models.ForeignKey(TeacherSalaryType, on_delete=models.SET_NULL, null=True)
    worked_hours = models.IntegerField(null=True)
    old_id = models.IntegerField(blank=True, null=True, unique=True)
    class_salary = models.IntegerField(default=0)

    class Meta:
        ordering = ['-month_date']


class TeacherBlackSalary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teacher_black_salary')
    black_salary = models.IntegerField(null=True)
    group = models.ForeignKey('group.Group', on_delete=models.CASCADE, null=True)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    month_date = models.DateField(null=True)
    status = models.BooleanField()


class TeacherSalaryList(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teacher_id_salary_list')
    salary_id = models.ForeignKey(TeacherSalary, on_delete=models.SET_NULL, null=True,
                                  related_name='salary_id_salary_list')
    payment = models.ForeignKey(PaymentTypes, on_delete=models.SET_NULL, null=True,
                                related_name='payment_id_salary_list')
    date = models.DateField(null=True)  # true qilish kerak
    comment = models.CharField(max_length=300)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='branch_id_salary_list')
    deleted = models.BooleanField(default=False)
    salary = models.IntegerField(default=0)
    old_id = models.IntegerField(blank=True, null=True, unique=True)

    class Meta:
        ordering = ['-date']


class TeacherGroupStatistics(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True,
                                related_name='teacher_id_teacher_group_statistics')
    reason = models.ForeignKey('group.GroupReason', on_delete=models.SET_NULL, null=True,
                               related_name='group_reason_id_teacher_group_statistics')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True,
                               related_name='branch_id_teacher_group_statistics')
    number_students = models.IntegerField()
    percentage = models.IntegerField()
    date = models.DateField(null=True, auto_now_add=False)  # true bolishi kerak

    class Meta:
        ordering = ['id']


class TeacherHistoryGroups(models.Model):
    group = models.ForeignKey('group.Group', on_delete=models.SET_NULL, null=True, related_name='group_teacher_history')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teacher_teacher_history')
    reason = models.CharField(max_length=50, null=True)
    joined_day = models.DateField()
    left_day = models.DateField(null=True)


class TeacherRequest(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Yuborildi'),
        ('review', 'Ko‘rib chiqilmoqda'),
        ('accepted', 'Qabul qilindi'),
        ('canceled', 'Bekor qilindi'),
    )

    teacher = models.ForeignKey(
        'Teacher',
        on_delete=models.CASCADE,
        related_name='requests'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.CASCADE,
        related_name='teacher_requests'
    )
    text = models.TextField()
    address = models.TextField(null=True)
    price = models.IntegerField(null=True)
    comment = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='sent'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)


class SatisfactionSurvey(models.Model):
    STATUS_CHOICES = (
        ("good", "Qoniqarli"),
        ("average", "Ortacha"),
        ("bad", "Qoniqarsiz"),
    )

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, null=True, blank=True)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    score = models.IntegerField(default=0)

    text = models.TextField(null=True, blank=True)
    datetime = models.DateTimeField()


# models.py

class TeacherContribution(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="contributions"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="given_contributions"
    )

    score = models.IntegerField()
    text = models.TextField(null=True, blank=True)

    datetime = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-datetime"]


class TeacherProfessionalism(models.Model):
    teacher = models.ForeignKey(
        "teachers.Teacher",
        on_delete=models.CASCADE,
        related_name="professionalism"
    )
    user = models.ForeignKey(  # kim baho qo‘ygan
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    score = models.IntegerField()
    text = models.TextField(null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher} - {self.score}"
