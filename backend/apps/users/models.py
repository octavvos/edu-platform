import random
import string
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        TEACHER = "teacher", "Teacher"
        STUDENT = "student", "Student"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT


class OTPCode(models.Model):
    class Purpose(models.TextChoices):
        REGISTER = "register", "Register"
        LOGIN = "login", "Login"
        RESET_PASSWORD = "reset_password", "Reset password"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otp_codes",
        null=True, blank=True,
    )
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=10)
    purpose = models.CharField(max_length=20, choices=Purpose.choices, default=Purpose.REGISTER)
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
        ttl = getattr(settings, "OTP_TTL_SECONDS", 300)
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

    def is_valid(self, code):
        return not self.is_used and not self.is_expired and self.code == code
