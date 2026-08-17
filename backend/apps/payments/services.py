from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.core.events import emit

from .models import LedgerEntry, Order, Payment
from .providers import get_provider

PLATFORM_COMMISSION_PERCENT = Decimal("30")  # P-07: default, admin panelidan sozlanadi


def create_order(*, user, course, idempotency_key: str, promo=None) -> Order:
    """P-02: Idempotency-Key — takroriy so'rov eski buyurtmani qaytaradi."""
    existing = Order.objects.filter(idempotency_key=idempotency_key).first()
    if existing:
        return existing

    amount = course.price
    if promo and promo.discount_percent:
        amount = amount * (Decimal(100) - promo.discount_percent) / Decimal(100)
    elif promo and promo.discount_amount:
        amount = max(Decimal(0), amount - promo.discount_amount)

    return Order.objects.create(
        user=user, course=course, promo=promo,
        amount=amount, currency=course.currency,
        idempotency_key=idempotency_key,
        status=Order.Status.PENDING if amount > 0 else Order.Status.PAID,
    )


def start_checkout(*, order: Order) -> dict:
    provider = get_provider()
    result = provider.create_checkout(order)
    if result.get("auto_completed"):
        mark_order_paid(order=order)
    return result


@transaction.atomic
def mark_order_paid(*, order: Order) -> Order:
    """P-03/P-08: webhook (yoki manual provider) chaqiradi — ledger yoziladi, event chiqadi."""
    if order.status == Order.Status.PAID:
        return order

    order.status = Order.Status.PAID
    order.save(update_fields=["status"])

    commission = (order.amount * PLATFORM_COMMISSION_PERCENT / Decimal(100)).quantize(Decimal("0.01"))
    teacher_share = order.amount - commission

    LedgerEntry.objects.create(
        account=LedgerEntry.Account.PLATFORM_REVENUE, debit=Decimal(0), credit=commission,
        ref_type="order", ref_id=order.id,
    )
    LedgerEntry.objects.create(
        account=LedgerEntry.Account.TEACHER_BALANCE, account_ref_id=order.course.teacher_id,
        debit=Decimal(0), credit=teacher_share,
        ref_type="order", ref_id=order.id,
    )

    emit(
        "payment_succeeded",
        order_id=str(order.id), user_id=str(order.user_id), course_id=str(order.course_id),
    )
    order.status = Order.Status.FULFILLED
    order.save(update_fields=["status"])
    return order


def refund_order(*, order: Order, admin_user) -> Order:
    """P-05: admin tasdig'i bilan qaytarish, enrollment yopiladi."""
    order.status = Order.Status.REFUNDED
    order.save(update_fields=["status"])

    LedgerEntry.objects.create(
        account=LedgerEntry.Account.PLATFORM_REVENUE, debit=order.amount, credit=Decimal(0),
        ref_type="refund", ref_id=order.id,
    )
    emit("order_refunded", order_id=str(order.id), user_id=str(order.user_id))
    return order
