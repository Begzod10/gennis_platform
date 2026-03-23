from django.db import models


class Party(models.Model):
    name = models.CharField(max_length=100)
    image = models.FileField(upload_to='parties/', null=True, blank=True)
    desc = models.TextField(null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    rating = models.FloatField(default=0.0)
    ball = models.IntegerField(default=0)


    students = models.ManyToManyField(
        'students.Student',
        blank=True,
        related_name='parties',
    )
    groups = models.ManyToManyField(
        'group.Group',
        blank=True,
        related_name='parties',
    )

    class Meta:
        ordering = ['-ball']

    def __str__(self):
        return self.name

    @property
    def members_count(self):
        return self.students.count()

    @property
    def wins_count(self):
        return self.competition_results.filter(is_winner=True).count()

    @property
    def tasks_count(self):
        return self.tasks.count()

    def display_name(self):

        if self.name:
            return self.name
        first_group = self.groups.select_related('class_number', 'color').first()
        if first_group:
            number = getattr(first_group.class_number, 'number', '')
            color  = getattr(first_group.color, 'name', '')
            return f"{number} {color}".strip() or "Nomsiz partiya"
        return "Nomsiz partiya"









class PartyMember(models.Model):

    ROLE_CHOICES = [
        ('captain', 'Kapitan'),
        ('member',  "A'zo"),
    ]
    STATUS_CHOICES = [
        ('active',   'Faol'),
        ('warning',  'Ogohlantirish'),
        ('inactive', 'Nofaol'),
    ]

    party   = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='memberships')
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        null=True,
        related_name='party_memberships',
    )
    role      = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    ball      = models.IntegerField(default=0)
    level     = models.CharField(max_length=50, blank=True)
    status    = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('party', 'student')
        ordering = ['-ball']

    def __str__(self):
        return f"{self.student} → {self.party.name} ({self.ball} ball)"


class PartyTask(models.Model):
    name         = models.CharField(max_length=200)
    desc         = models.TextField(null=True, blank=True)
    ball         = models.IntegerField(null=True, blank=True)
    deadline     = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    parties      = models.ManyToManyField(Party, blank=True, related_name='tasks')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class PartyTaskGrade(models.Model):
    task      = models.ForeignKey(PartyTask, on_delete=models.CASCADE, related_name='grades')
    party     = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='grades')
    ball      = models.IntegerField(default=0)
    graded_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('task', 'party')

    def __str__(self):
        return f"{self.task.name} | {self.party.name} = {self.ball}"




class Competition(models.Model):
    name       = models.CharField(max_length=200)
    emoji      = models.CharField(max_length=10, default='🏆')
    color      = models.CharField(max_length=20, default='#10b981')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


QUARTER_CHOICES = [
    ('1-chorak', '1-chorak'),
    ('2-chorak', '2-chorak'),
    ('3-chorak', '3-chorak'),
    ('4-chorak', '4-chorak'),
]


class CompetitionResult(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='results')
    party       = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='competition_results')
    quarter     = models.CharField(max_length=20, choices=QUARTER_CHOICES)
    ball        = models.IntegerField(default=0)
    note        = models.CharField(max_length=300, blank=True)
    is_winner   = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.competition.name} | {self.party.name} | {self.quarter} = {self.ball}"
