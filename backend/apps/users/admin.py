from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import OTPCode, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "phone", "role", "is_phone_verified", "is_staff")
    list_filter = ("role", "is_phone_verified", "is_staff", "is_active")
    search_fields = ("username", "email", "phone", "first_name", "last_name")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Qo'shimcha", {"fields": ("role", "phone", "is_phone_verified", "bio", "avatar")}),
    )


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ("phone", "code", "purpose", "is_used", "created_at", "expires_at")
    list_filter = ("purpose", "is_used")
    search_fields = ("phone",)
