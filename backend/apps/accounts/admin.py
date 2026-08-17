from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import LoginAttemptLog, OTPCode, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "phone", "role", "status", "is_phone_verified", "is_staff")
    list_filter = ("role", "status", "is_phone_verified", "is_staff", "is_active")
    search_fields = ("username", "email", "phone", "first_name", "last_name")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Qo'shimcha", {"fields": ("role", "status", "phone", "is_phone_verified", "bio", "avatar")}),
    )


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ("phone", "code", "purpose", "attempts", "is_used", "created_at", "expires_at")
    list_filter = ("purpose", "is_used")
    search_fields = ("phone",)


@admin.register(LoginAttemptLog)
class LoginAttemptLogAdmin(admin.ModelAdmin):
    list_display = ("username_or_phone", "ip_address", "was_successful", "created_at")
    list_filter = ("was_successful",)
    search_fields = ("username_or_phone", "ip_address")
