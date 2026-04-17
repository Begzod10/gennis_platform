from datetime import datetime

from django.conf import settings
from django.db import models

from payments.models import PaymentTypes
from subjects.models import Subject
from teachers.models import Teacher
from user.serializers import (CustomUser, Branch)


class Student(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_user')
    subject = models.ManyToManyField(Subject, blank=True)
    total_payment_month = models.IntegerField(null=True)
    extra_payment = models.CharField(null=True)
    shift = models.CharField(max_length=50, null=True)
    debt_status = models.BigIntegerField(null=True)
    parents_number = models.CharField(max_length=250, null=True)
    representative_name = models.CharField(max_length=255, null=True)
    representative_surname = models.CharField(max_length=255, null=True)
    telegram_id = models.BigIntegerField(null=True)
    mother_choose = models.BooleanField(default=False)
    father_choose = models.BooleanField(default=False)
    father_passport_number = models.CharField(max_length=255, null=True, blank=True)
    mother_passport_number = models.CharField(max_length=255, null=True, blank=True)
    father_telegram_id = models.BigIntegerField(null=True)
    mother_telegram_id = models.BigIntegerField(null=True)
    parents_fullname = models.CharField(max_length=255, null=True, blank=True)
    old_id = models.IntegerField(null=True, unique=True)
    turon_old_id = models.IntegerField(null=True, unique=True)
    old_money = models.BigIntegerField(null=True)
    student_seria = models.CharField(max_length=255, null=True)
    student_seria_num = models.CharField(null=True)
    region = models.CharField(max_length=255, null=True)
    district = models.CharField(max_length=255, null=True)
    old_school = models.CharField(max_length=255, null=True)
    parent_region = models.CharField(max_length=255, null=True)
    parent_seria = models.CharField(max_length=255, null=True)
    parent_seria_num = models.CharField(null=True)
    born_date = models.DateField(null=True)
    group_time_table = models.ManyToManyField('time_table.GroupTimeTable', blank=True)
    system = models.ForeignKey('system.System', on_delete=models.SET_NULL, null=True)
    class_number = models.ForeignKey('classes.ClassNumber', on_delete=models.SET_NULL, null=True)
    joined_group = models.DateField(null=True)

    def __str__(self):
        return f"{self.user.name} {self.user.surname} {self.id}"


class StudentExamResult(models.Model):
    title = models.CharField(max_length=255)  # Final, Midterm, Mock va hk

    group = models.ForeignKey(
        'group.Group',
        on_delete=models.CASCADE,
        related_name="exam_results"
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="exam_results"
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="exam_results"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="exam_results"
    )

    score = models.FloatField(default=0)

    datetime = models.DateTimeField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-datetime"]


class StudentCharity(models.Model):
    charity_sum = models.IntegerField()
    name = models.CharField(max_length=200, blank=True, null=True)
    group = models.ForeignKey('group.Group', on_delete=models.SET_NULL, null=True, related_name='group_id_charity')
    added_data = models.DateField(auto_now_add=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='charity_student_id')
    old_id = models.IntegerField(null=True)
    branch = models.ForeignKey('branch.Branch', on_delete=models.SET_NULL, null=True)


class StudentPayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    payment_type = models.ForeignKey(PaymentTypes, on_delete=models.SET_NULL, null=True)
    payment_sum = models.IntegerField(default=0)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    added_data = models.DateField(auto_now_add=True)
    date = models.DateField(null=True)
    status = models.BooleanField()
    extra_payment = models.IntegerField(null=True, default=0)
    deleted = models.BooleanField(default=False)
    old_id = models.IntegerField(unique=True, null=True)
    reason = models.CharField(max_length=255, null=True)
    attendance = models.ForeignKey('attendances.AttendancePerMonth', on_delete=models.SET_NULL, null=True)


class DeletedNewStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='deleted_student_student_new')
    created = models.DateField(auto_now_add=True)
    comment = models.CharField(null=True)  # old_id = models.IntegerField(unique=True, null=True)


class StudentHistoryGroups(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, related_name='student_student_history')
    group = models.ForeignKey('group.Group', on_delete=models.SET_NULL, null=True, related_name='group_student_history')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='teacher_student_history')
    reason = models.CharField(max_length=50, null=True)
    joined_day = models.DateField()
    left_day = models.DateField(null=True)
    old_id = models.IntegerField(null=True)


class DeletedStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='deleted_student_student', null=True)
    group = models.ForeignKey('group.Group', on_delete=models.CASCADE, related_name='deleted_student_group', null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='deleted_student_teacher', null=True)
    group_reason = models.ForeignKey('group.GroupReason', on_delete=models.SET_NULL, null=True,
                                     related_name='deleted_student_group_reason')

    deleted_date = models.DateField(default=datetime.now)
    old_id = models.IntegerField(unique=True, null=True)
    comment = models.CharField(max_length=255, null=True)
    deleted = models.BooleanField(default=False)


class ContractStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='contract_student_id')
    created_date = models.DateField(auto_now_add=True)
    expire_date = models.DateField(null=True)
    father_name = models.CharField(max_length=255)
    given_place = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    passport_series = models.CharField(max_length=255)
    given_time = models.CharField(max_length=255)
    contract = models.FileField(upload_to='contracts')
    old_id = models.IntegerField(unique=True, null=True)
    year = models.DateField(null=True)  # Add this field


class StudentSubject(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='student_subjects')
    hours = models.IntegerField(null=True, default=0)
    count = models.IntegerField(null=True, default=0)
    group_subjects = models.ForeignKey('group.GroupSubjects', on_delete=models.CASCADE, null=True,
                                       related_name='student_subjects')


class StudentSubjectCount(models.Model):
    student_subjects = models.ForeignKey(StudentSubject, on_delete=models.CASCADE, null=True,
                                         related_name='student_subject_count')
    class_time_table = models.ForeignKey('school_time_table.ClassTimeTable', on_delete=models.CASCADE, null=True,
                                         related_name='student_subject_count')
    date = models.DateField()


class CallLog(models.Model):
    CATEGORY_CHOICES = (
        ('debtor', 'Debtor'),
        ('lead', 'Lead'),
        ('new_student', 'New Student'),
    )

    STATUS_CHOICES = (
        ('answered', 'Answered'),
        ('not_answered', 'Not answered'),
    )

    # VATS tomonidan kelgan ma'lumotlar
    vats_call_id = models.CharField(max_length=100, null=True, blank=True, unique=True,
                                    help_text="VATS'dan kelgan callid")
    vats_status = models.CharField(max_length=50, null=True, blank=True,
                                   help_text="VATS call statusi: Success, missed, Cancel, Busy...")
    vats_duration = models.PositiveIntegerField(null=True, blank=True, help_text="Suhbat davomiyligi (soniya)")
    vats_wait = models.PositiveIntegerField(null=True, blank=True, help_text="Kutish vaqti (soniya)")
    vats_phone = models.CharField(max_length=30, null=True, blank=True, help_text="Mijoz telefon raqami (VATS'dan)")
    vats_user = models.CharField(max_length=100, null=True, blank=True, help_text="VATS xodim identifikatori")
    vats_start = models.DateTimeField(null=True, blank=True, help_text="VATS'da qo'ng'iroq boshlangan vaqt")
    vats_type = models.CharField(max_length=10, null=True, blank=True, help_text="in yoki out")

    # CRM uchun ma'lumotlar
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, null=True, blank=True)
    lead = models.ForeignKey('lead.Lead', on_delete=models.CASCADE, null=True, blank=True)

    comment = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    called_at = models.DateTimeField(auto_now_add=True)
    next_call_date = models.DateField(null=True, blank=True)

    # Audio - VATS'dan link yoki mahalliy fayl
    audio = models.FileField(upload_to='call_records/', null=True, blank=True)
    audio_url = models.URLField(null=True, blank=True, help_text="VATS'dan kelgan audio havolasi")

    created_at = models.DateTimeField(auto_now_add=True)

    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.category} | {self.status} | {self.called_at.strftime('%d.%m.%Y %H:%M')}"


class CallStatistic(models.Model):
    CATEGORY_CHOICES = (
        ('debtor', 'Debtor'),
        ('lead', 'Lead'),
        ('new_student', 'New Student'),
    )

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    date = models.DateField()  # bugungi sana

    total = models.PositiveIntegerField(default=0)
    called = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('branch', 'category', 'date')

    @property
    def percentage(self):
        if self.total == 0:
            return 0
        return round((self.called / self.total) * 100, 1)

    def __str__(self):
        return f"{self.branch} | {self.category} | {self.date} | {self.called}/{self.total}"
