import random
import string
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    TZ 5.5 (User model) + D-01 (UUID PK) + D-12 (utm_source).

    Eslatma: TZ 3-bo'limida rollar `rbac.RoleAssignment` orqali granular
    boshqariladi (ko'p rolga ega bo'lish mumkin, R-04). Amaliy qulaylik
    uchun bitta asosiy `role` maydoni ham saqlanadi (ro'yxatdan o'tishda
    tanlanadi, RoleAssignment bilan sinxron seed qilinadi) — frontend va
    oddiy tekshiruvlar shu orqali ishlaydi, granular ruxsatlar esa
    apps.rbac orqali.
    """

    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"
        MENTOR = "mentor", "Mentor"
        ADMIN = "admin", "Administrator"
        SUPER_ADMIN = "super_admin", "Super-admin"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        BLOCKED = "blocked", "Blocked"
        PENDING_DELETION = "pending_deletion", "Pending deletion"  # U-06: 30 kunlik grace davr
        DELETED = "deleted", "Deleted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=120, blank=True)

    # U-02
    locale = models.CharField(max_length=10, default="uz")
    timezone = models.CharField(max_length=64, default="Asia/Tashkent")
    theme = models.CharField(max_length=10, default="light")

    # D-12: marketing moduli kelganda tarixiy data bo'lishi uchun hozirdan saqlanadi
    utm_source = models.CharField(max_length=120, blank=True)
    utm_medium = models.CharField(max_length=120, blank=True)
    utm_campaign = models.CharField(max_length=120, blank=True)

    organization_id = models.UUIDField(null=True, blank=True, db_index=True)

    deletion_requested_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role in (self.Role.ADMIN, self.Role.SUPER_ADMIN) or self.is_superuser

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN or self.is_superuser

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_mentor(self):
        return self.role == self.Role.MENTOR

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT


class OTPCode(models.Model):
    """A-04: 6 raqam, TTL 120 sekund, 3 ta urinish, 1 raqamga soatiga max 3 SMS."""

    class Purpose(models.TextChoices):
        REGISTER = "register", "Register"
        LOGIN = "login", "Login"
        RESET_PASSWORD = "reset_password", "Reset password"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otp_codes",
        null=True, blank=True,
    )
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=10)
    purpose = models.CharField(max_length=20, choices=Purpose.choices, default=Purpose.REGISTER)
    attempts = models.PositiveSmallIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP({self.phone}, {self.purpose})"

    @classmethod
    def generate_code(cls, length=None):
        length = length or getattr(settings, "OTP_CODE_LENGTH", 6)
        return "".join(random.choices(string.digits, k=length))

    @classmethod
    def create_for_phone(cls, phone, purpose=Purpose.REGISTER, user=None):
        ttl = getattr(settings, "OTP_TTL_SECONDS", 120)
        return cls.objects.create(
            user=user,
            phone=phone,
            code=cls.generate_code(),
            purpose=purpose,
            expires_at=timezone.now() + timedelta(seconds=ttl),
        )

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    MAX_ATTEMPTS = 3

    def is_valid(self, code):
        if self.is_used or self.is_expired or self.attempts >= self.MAX_ATTEMPTS:
            return False
        return self.code == code


class LoginAttemptLog(models.Model):
    """A-10: barcha kirish urinishlari IP va User-Agent bilan logga yoziladi."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username_or_phone = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    was_successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
