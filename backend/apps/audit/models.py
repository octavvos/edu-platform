import uuid

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """AD-08: kim, qachon, nimani o'zgartirdi (before/after) — append-only."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="audit_logs", null=True, blank=True,
    )
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=64, blank=True)
    before = models.JSONField(default=dict, blank=True)
    after = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True)  # AD-01: impersonate uchun sabab majburiy
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.actor} {self.action} {self.object_type}:{self.object_id}"


class FeatureFlag(models.Model):
    """AD-07: feature flags."""

    key = models.CharField(max_length=100, unique=True)
    is_enabled = models.BooleanField(default=False)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.key} ({'on' if self.is_enabled else 'off'})"
