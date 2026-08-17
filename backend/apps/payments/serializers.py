from rest_framework import serializers

from .models import LedgerEntry, Order, Payment, Promo


class OrderSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "user", "course", "course_title", "promo",
            "amount", "currency", "status", "idempotency_key", "created_at",
        )
        read_only_fields = ("id", "user", "amount", "currency", "status", "created_at")


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "order", "provider", "provider_txn_id", "status", "created_at")
        read_only_fields = fields


class LedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = ("id", "account", "account_ref_id", "debit", "credit", "ref_type", "ref_id", "created_at")
        read_only_fields = fields


class PromoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo
        fields = ("id", "code", "discount_percent", "discount_amount", "valid_from", "valid_to", "usage_limit")
