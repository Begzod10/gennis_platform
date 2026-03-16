from django.db import models



class Report(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    program_type = models.CharField(max_length=100, null=True, blank=True, default="Turon")
    text = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name or "Report"

    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"