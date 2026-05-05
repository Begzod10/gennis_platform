from django.db import models
from django.utils.text import slugify
import uuid
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class News(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    date = models.DateField()
    image_url = models.URLField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='news/images/', null=True, blank=True)
    published = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while News.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


def generate_application_id():
    from django.utils import timezone
    year = timezone.now().year
    unique = str(uuid.uuid4()).split('-')[0].upper()
    return f"APP-{year}-{unique}"


class Admission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('enrolled', 'Enrolled'),
        ('rejected', 'Rejected'),
    )

    application_id = models.CharField(
        max_length=50, unique=True, default=generate_application_id
    )
    student_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    grade = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    notes = models.TextField(null=True, blank=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.application_id} - {self.student_name}"

    class Meta:
        ordering = ['-created_at']


class ContactMessage(models.Model):
    STATUS_CHOICES = (
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('replied', 'Replied'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    message = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='unread'
    )
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

    class Meta:
        ordering = ['-created_at']


def generate_job_application_id():
    from django.utils import timezone
    year = timezone.now().year
    unique = str(uuid.uuid4()).split('-')[0].upper()
    return f"JOB-{year}-{unique}"


class JobPosition(models.Model):
    TYPE_CHOICES = (
        ('Academic', 'Academic'),
        ('Non-Academic', 'Non-Academic'),
    )

    title = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    location = models.CharField(max_length=100, null=True, blank=True)
    employment_type = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    requirements = models.JSONField(default=list, blank=True)
    posted_date = models.DateField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class CareerApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewing', 'Reviewing'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    )

    application_id = models.CharField(
        max_length=50, unique=True, default=generate_job_application_id
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20)
    position = models.ForeignKey(
        JobPosition, on_delete=models.SET_NULL, null=True, blank=True
    )
    cv_file = models.FileField(upload_to='careers/cvs/', null=True)
    cover_letter = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending'
    )
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application_id} - {self.name}"

    class Meta:
        ordering = ['-created_at']


class TalentPool(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20)
    expertise = models.CharField(max_length=255, null=True, blank=True)
    cv_file = models.FileField(upload_to='careers/talent-pool/', null=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.expertise}"

    class Meta:
        ordering = ['-created_at']
