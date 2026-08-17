import uuid

from django.conf import settings
from django.db import models


class Promo(models.Model):
    """P-06: foiz/summa, amal muddati, foydalanish limiti, kurslar bo'yicha cheklov."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=40, unique=True)
    discount_percent = models.PositiveSmallIntegerField(null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    times_used = models.PositiveIntegerField(default=0)
    courses = models.ManyToManyField("courses.Course", blank=True, related_name="promos")

    def __str__(self):
        return self.code


class Order(models.Model):
    """P-10: created -> pending -> paid -> fulfilled; failed / expired / refunded."""

    class Status(models.TextChoices):
        CREATED = "created", "Yaratildi"
        PENDING = "pending", "Kutilmoqda"
        PAID = "paid", "To'landi"
        FULFILLED = "fulfilled", "Bajarildi"
        FAILED = "failed", "Muvaffaqiyatsiz"
        EXPIRED = "expired", "Muddati o'tgan"
        REFUNDED = "refunded", "Qaytarildi"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="orders")
    promo = models.ForeignKey(Promo, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="UZS")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)

    # P-02: idempotent to'lov
    idempotency_key = models.CharField(max_length=64, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order({self.id}, {self.status})"


class Payment(models.Model):
    """P-01/P-03/P-04: karta ma'lumoti saqlanmaydi, webhook orqali tasdiqlanadi."""

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        SUCCESS = "success", "Muvaffaqiyatli"
        FAILED = "failed", "Muvaffaqiyatsiz"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    provider = models.CharField(max_length=30, default="manual")
    provider_txn_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    raw_payload = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment({self.provider}, {self.status})"


class LedgerEntry(models.Model):
    """P-08: double-entry (ikki yozuvli) — append-only, balans faqat shundan hisoblanadi."""

    class Account(models.TextChoices):
        PLATFORM_REVENUE = "platform_revenue", "Platforma daromadi"
        TEACHER_BALANCE = "teacher_balance", "O'qituvchi balansi"
        STUDENT_WALLET = "student_wallet", "Talaba hisobi"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.CharField(max_length=30, choices=Account.choices)
    account_ref_id = models.UUIDField(null=True, blank=True)  # masalan teacher user id
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ref_type = models.CharField(max_length=30)  # "order", "payout", "refund"
    ref_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"LedgerEntry({self.account}, debit={self.debit}, credit={self.credit})"
