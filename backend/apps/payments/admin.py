from django.contrib import admin

from .models import LedgerEntry, Order, Payment, Promo


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "course", "amount", "currency", "status", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("user__username", "course__title", "idempotency_key")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "provider", "status", "created_at")
    list_filter = ("provider", "status")


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("account", "debit", "credit", "ref_type", "ref_id", "created_at")
    list_filter = ("account", "ref_type")


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "discount_amount", "usage_limit", "times_used")
