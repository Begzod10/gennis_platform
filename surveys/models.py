from django.db import models
from django.conf import settings


class Survey(models.Model):
    TARGET_CHOICES = [
        ('all', 'Hammaga'),
        ('student', 'Studentlarga'),
        ('teacher', "O'qituvchilarga"),
        ('parent', 'Ota-onalarga'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    target_role = models.CharField(max_length=20, choices=TARGET_CHOICES, default='all')
    deadline = models.DateField()
    is_active = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_surveys'
    )
    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='surveys'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def status(self):
        from django.utils import timezone
        if not self.is_active:
            return 'inactive'
        if self.deadline < timezone.now():
            return 'expired'
        return 'active'


class SurveyQuestion(models.Model):
    TYPE_CHOICES = [
        ('yes_no', "Ha / Yo'q"),
        ('star', 'Yulduz reytingi'),
        ('test', "Ko'p variantli"),
        ('short_answer', 'Qisqa javob'),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.survey.title} — {self.text[:50]}"


class SurveyQuestionOption(models.Model):
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


class SurveySubmission(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', "O'qituvchi"),
        ('parent', 'Ota-ona'),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='submissions')
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='survey_submissions'
    )
    respondent_role = models.CharField(max_length=10, choices=ROLE_CHOICES, null=True, blank=True)

    student_ref = models.ForeignKey(
        'students.Student',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='survey_submissions'
    )
    teacher_ref = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='survey_submissions_as_respondent'
    )
    parent_ref = models.ForeignKey(
        'parents.Parent',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='survey_submissions'
    )

    branch = models.ForeignKey(
        'branch.Branch',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='survey_submissions'
    )

    target_teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='received_submissions'
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('survey', 'respondent', 'target_teacher')

    def __str__(self):
        return f"[{self.respondent_role}] {self.respondent} → {self.survey.title}"


class SurveyAnswer(models.Model):
    submission = models.ForeignKey(SurveySubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    value = models.TextField()

    def __str__(self):
        return f"{self.question.text[:30]}: {self.value}"