from django.db import models

from students.models import Student
from teachers.models import Teacher
from group.models import Group
from flows.models import Flow


class AttendancePerMonth(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    status = models.BooleanField(default=False)
    total_debt = models.IntegerField(default=0, null=True)
    total_salary = models.IntegerField(default=0, null=True)
    ball_percentage = models.IntegerField(default=0, null=True)
    month_date = models.DateField(null=True)
    total_charity = models.IntegerField(default=0, null=True)
    remaining_debt = models.IntegerField(default=0, null=True)
    payment = models.IntegerField(default=0)
    system = models.ForeignKey('system.System', on_delete=models.CASCADE, null=True)
    old_id = models.IntegerField(null=True, unique=True)
    remaining_salary = models.IntegerField(default=0, null=True)
    taken_salary = models.IntegerField(default=0, null=True)
    present_days = models.IntegerField(default=0, null=True)
    absent_days = models.IntegerField(default=0, null=True)
    scored_days = models.IntegerField(default=0, null=True)
    discount = models.IntegerField(null=True, default=0)
    discount_percentage = models.IntegerField(null=True, default=0)
    old_money = models.CharField(max_length=255, null=True)


class AttendancePerDay(models.Model):
    attendance_per_month = models.ForeignKey(AttendancePerMonth, on_delete=models.CASCADE, null=True)
    debt_per_day = models.IntegerField(null=True)
    salary_per_day = models.IntegerField(null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    charity_per_day = models.IntegerField(null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    day = models.DateField(null=True)
    homework_ball = models.IntegerField(null=True)
    dictionary_ball = models.IntegerField(null=True)
    activeness_ball = models.IntegerField(null=True)
    average = models.IntegerField(null=True)
    status = models.BooleanField(default=False)
    old_id = models.IntegerField(null=True, unique=True)
    reason = models.CharField(null=True, blank=True)
    teacher_ball = models.IntegerField(null=True)


class GroupAttendancesPerMonth(models.Model):
    total_debt = models.IntegerField(null=True)
    total_salary = models.IntegerField(null=True)
    month_date = models.DateField(null=True)
    total_charity = models.IntegerField(null=True)
    remaining_debt = models.IntegerField(null=True)
    payment = models.IntegerField(null=True)
    remaining_salary = models.IntegerField(null=True)
    taken_salary = models.IntegerField(null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class StudentMonthlySummary(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    year = models.IntegerField()
    month = models.IntegerField()

    stats = models.JSONField(default=dict)
    # {"present": 20, "absent": 3, "total_days": 30}

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'group', 'year', 'month')


class StudentDailyAttendance(models.Model):
    monthly_summary = models.ForeignKey(
        StudentMonthlySummary,
        on_delete=models.CASCADE,
        related_name="daily_records"
    )

    day = models.DateField()
    status = models.BooleanField(default=False)  # True = keldi, False = kelmadi
    reason = models.CharField(max_length=255, null=True, blank=True)
    entry_time = models.DateTimeField(null=True)
    leave_time = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('monthly_summary', 'day')


class GroupMonthlySummary(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="monthly_summaries")
    year = models.IntegerField()
    month = models.IntegerField()
    stats = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ("group", "year", "month")

    def __str__(self):
        return f"{self.group.name} - {self.year}/{self.month}"


class StudentScoreByTeacher(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    flow = models.ForeignKey(Flow, on_delete=models.CASCADE, null=True)
    homework = models.IntegerField(default=0)
    activeness = models.IntegerField(default=0)
    status = models.BooleanField(default=False)
    average = models.IntegerField(default=0)
    day = models.DateField(auto_now_add=True)

