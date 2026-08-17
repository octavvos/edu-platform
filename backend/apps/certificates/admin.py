from django.contrib import admin

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("code", "enrollment", "issued_at")
    search_fields = ("code",)
