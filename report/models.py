from django.db import models
from django.conf import settings




class Report(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    program_type = models.CharField(max_length=100, null=True, blank=True, default="Turon")
    text = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name or "Report"


class AdminRequest(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    branch = models.ForeignKey('branch.Branch', on_delete=models.CASCADE, related_name='admin_requests', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_requests', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Admin Request"
        verbose_name_plural = "Admin Requests"


class RequestComment(models.Model):
    request = models.ForeignKey(AdminRequest, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='request_comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.request}"

    class Meta:
        verbose_name = "Request Comment"
        verbose_name_plural = "Request Comments"
