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
    locale = models.CharField(max_length=10, default='uz')
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


class ComponentDefinition(models.Model):
    key = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    props_schema = models.JSONField(default=dict, blank=True)
    default_props = models.JSONField(default=dict, blank=True)
    allowed_roles = models.JSONField(default=list, blank=True)
    is_layout = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

    class Meta:
        ordering = ['key']


class ThemeSetting(models.Model):
    MODE_CHOICES = (
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System'),
    )

    name = models.CharField(max_length=120)
    mode = models.CharField(max_length=12, choices=MODE_CHOICES, default='light')
    tokens = models.JSONField(default=dict, blank=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-is_default', 'name']


class Menu(models.Model):
    key = models.SlugField(max_length=80)
    name = models.CharField(max_length=120)
    items = models.JSONField(default=list, blank=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

    class Meta:
        ordering = ['key']
        constraints = [
            models.UniqueConstraint(
                fields=['key', 'branch'],
                name='unique_menu_key_branch',
            ),
            models.UniqueConstraint(
                fields=['key'],
                condition=models.Q(branch__isnull=True),
                name='unique_global_menu_key',
            ),
        ]


class ReusableBlock(models.Model):
    key = models.SlugField(max_length=80)
    name = models.CharField(max_length=120)
    sections = models.JSONField(default=list, blank=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

    class Meta:
        ordering = ['key']
        constraints = [
            models.UniqueConstraint(
                fields=['key', 'branch'],
                name='unique_reusable_block_key_branch',
            ),
            models.UniqueConstraint(
                fields=['key'],
                condition=models.Q(branch__isnull=True),
                name='unique_global_reusable_block_key',
            ),
        ]


class Page(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )

    slug = models.SlugField(max_length=120)
    title = models.CharField(max_length=180)
    locale = models.CharField(max_length=12, default='uz')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft')
    seo = models.JSONField(default=dict, blank=True)
    permissions = models.JSONField(default=dict, blank=True)
    cache = models.JSONField(default=dict, blank=True)
    theme = models.ForeignKey(
        ThemeSetting, on_delete=models.SET_NULL, null=True, blank=True, related_name='pages'
    )
    navigation = models.ForeignKey(
        Menu, on_delete=models.SET_NULL, null=True, blank=True, related_name='navigation_pages'
    )
    footer = models.ForeignKey(
        ReusableBlock, on_delete=models.SET_NULL, null=True, blank=True, related_name='footer_pages'
    )
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    version = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.slug} ({self.locale})'

    class Meta:
        ordering = ['slug', 'locale']
        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'locale', 'branch'],
                name='unique_page_slug_locale_branch',
            ),
            models.UniqueConstraint(
                fields=['slug', 'locale'],
                condition=models.Q(branch__isnull=True),
                name='unique_global_page_slug_locale',
            ),
        ]


class PageSection(models.Model):
    page = models.ForeignKey(Page, related_name='sections', on_delete=models.CASCADE)
    component = models.ForeignKey(ComponentDefinition, on_delete=models.PROTECT)
    parent = models.ForeignKey(
        'self', related_name='children', on_delete=models.CASCADE, null=True, blank=True
    )
    section_id = models.SlugField(max_length=120, blank=True)
    props = models.JSONField(default=dict, blank=True)
    layout = models.JSONField(default=dict, blank=True)
    visibility = models.JSONField(default=dict, blank=True)
    responsive = models.JSONField(default=dict, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.page.slug}: {self.component.key}'

    class Meta:
        ordering = ['sort_order', 'id']


class DynamicForm(models.Model):
    key = models.SlugField(max_length=80)
    title = models.CharField(max_length=160)
    fields = models.JSONField(default=list, blank=True)
    submit_endpoint = models.CharField(max_length=180)
    success_message = models.CharField(max_length=255, blank=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

    class Meta:
        ordering = ['key']
        constraints = [
            models.UniqueConstraint(
                fields=['key', 'branch'],
                name='unique_dynamic_form_key_branch',
            ),
            models.UniqueConstraint(
                fields=['key'],
                condition=models.Q(branch__isnull=True),
                name='unique_global_dynamic_form_key',
            ),
        ]


class MediaAsset(models.Model):
    file = models.FileField(upload_to='cms/')
    alt = models.CharField(max_length=180, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.alt or self.file.name


class SchoolStatistic(models.Model):
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, blank=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    locale = models.CharField(max_length=10, default='uz')
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.label} ({self.locale})"

    class Meta:
        ordering = ['sort_order']


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    text = models.TextField()
    image = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    locale = models.CharField(max_length=10, default='uz')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.locale})"


class WhyChooseItem(models.Model):
    text = models.CharField(max_length=255)
    icon = models.CharField(max_length=50, blank=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    locale = models.CharField(max_length=10, default='uz')
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.text[:30]} ({self.locale})"

    class Meta:
        ordering = ['sort_order']


class Partner(models.Model):
    CATEGORY_CHOICES = (
        ('academic', 'Academic'),
        ('industry', 'Industry'),
        ('cultural', 'Cultural'),
        ('community', 'Community'),
    )
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='partners/', null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    locale = models.CharField(max_length=10, default='uz')
    sort_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.locale})"

    class Meta:
        ordering = ['sort_order']


class Leadership(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    message = models.TextField()
    image = models.ImageField(upload_to='leadership/', null=True, blank=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    locale = models.CharField(max_length=10, default='uz')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.locale})"


class SectionContent(models.Model):
    SECTION_CHOICES = (
        ('hero', 'Hero'),
        ('who_we_are', 'Who We Are'),
        ('philosophy', 'Philosophy'),
        ('education_approach', 'Education Approach'),
        ('careers_intro', 'Careers Intro'),
        ('admissions_intro', 'Admissions Intro'),
        ('contact_info', 'Contact Info'),
        ('footer', 'Footer'),
        ('campus_life', 'Campus Life'),
        ('vision_mission', 'Vision & Mission'),
        ('leadership_governance', 'Leadership & Governance'),
        ('why_tis_differ', 'Why TIS Differentiators'),
        ('education_skills', 'Education Skills'),
        ('partnership_network', 'Partnership Network'),
    )
    section = models.CharField(max_length=100)
    title = models.CharField(max_length=255, blank=True)
    subtitle = models.TextField(blank=True)
    content = models.TextField(blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    locale = models.CharField(max_length=10, default='uz')

    def __str__(self):
        return f"{self.section} - {self.locale}"

    class Meta:
        unique_together = ('section', 'locale', 'branch')


class GlobalSetting(models.Model):
    key = models.SlugField(max_length=80)
    value = models.JSONField(default=dict, blank=True)
    branch = models.ForeignKey(
        'branch.Branch', on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['key', 'branch'],
                name='unique_global_setting_key_branch',
            ),
            models.UniqueConstraint(
                fields=['key'],
                condition=models.Q(branch__isnull=True),
                name='unique_global_setting_key',
            ),
        ]


class Translation(models.Model):
    key = models.SlugField(max_length=120, unique=True)
    uz = models.TextField(blank=True)
    ru = models.TextField(blank=True)
    en = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

    class Meta:
        ordering = ['key']
