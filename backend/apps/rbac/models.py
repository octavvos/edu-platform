import uuid

from django.conf import settings
from django.db import models


class Permission(models.Model):
    """R-01: granular permission-lar (course.publish, payment.refund, ...)."""

    codename = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["codename"]

    def __str__(self):
        return self.codename


class Role(models.Model):
    """R-03: rollarni admin panelidan yaratish/tahrirlash/huquq biriktirish."""

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    permissions = models.ManyToManyField(Permission, related_name="roles", blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RoleAssignment(models.Model):
    """
    R-02/R-04: har bir huquq scope'ga ega (global/course/organization),
    foydalanuvchi bir vaqtda bir nechta rolga ega bo'lishi mumkin.
    """

    class ScopeType(models.TextChoices):
        GLOBAL = "global", "Global"
        COURSE = "course", "Course"
        ORGANIZATION = "organization", "Organization"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="role_assignments")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="assignments")
    scope_type = models.CharField(max_length=20, choices=ScopeType.choices, default=ScopeType.GLOBAL)
    scope_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "role", "scope_type", "scope_id")

    def __str__(self):
        scope = f"{self.scope_type}:{self.scope_id}" if self.scope_id else self.scope_type
        return f"{self.user} -> {self.role} ({scope})"
