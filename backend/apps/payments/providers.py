"""
TZ 4.10/D-11: to'lov provayder abstraksiyasi. `PaymeProvider` haqiqiy
Payme merchant kalitlari (`PAYME_MERCHANT_ID`, `PAYME_SECRET_KEY`)
ulanmaguncha ishlamaydi — sozlansa, faqat shu fayl almashadi,
`services.py`/API o'zgarmaydi (Q-03).

Lokal/demo muhitda `PAYMENT_PROVIDER=manual` (standart) — buyurtma
darhol "to'landi" deb belgilanadi, real karta/pul harakati yo'q.
"""

from abc import ABC, abstractmethod

from django.conf import settings

from .models import Order, Payment


class PaymentProvider(ABC):
    @abstractmethod
    def create_checkout(self, order: Order) -> dict:
        """To'lov sahifasiga yo'naltirish uchun ma'lumot qaytaradi."""

    @abstractmethod
    def verify_webhook(self, headers: dict, body: bytes) -> bool:
        """P-04: webhook imzosini (HMAC) tekshiradi."""


class ManualTestProvider(PaymentProvider):
    """Faqat DEBUG/demo uchun — Payme hisobi ulanmaguncha to'lovni darhol yopadi."""

    def create_checkout(self, order: Order) -> dict:
        payment = Payment.objects.create(
            order=order, provider="manual", status=Payment.Status.SUCCESS,
            provider_txn_id=f"manual-{order.id}",
        )
        return {"checkout_url": None, "auto_completed": True, "payment_id": str(payment.id)}

    def verify_webhook(self, headers: dict, body: bytes) -> bool:
        return True


class PaymeProvider(PaymentProvider):
    """I-01: haqiqiy Payme integratsiyasi — merchant kalitlari kelganda to'ldiriladi."""

    def create_checkout(self, order: Order) -> dict:
        if not getattr(settings, "PAYME_MERCHANT_ID", ""):
            raise NotImplementedError(
                "Payme merchant kalitlari sozlanmagan (PAYME_MERCHANT_ID / PAYME_SECRET_KEY)."
            )
        raise NotImplementedError("Payme checkout integratsiyasi hali ulanmagan.")

    def verify_webhook(self, headers: dict, body: bytes) -> bool:
        raise NotImplementedError("Payme webhook HMAC tekshiruvi hali ulanmagan.")


def get_provider() -> PaymentProvider:
    provider_name = getattr(settings, "PAYMENT_PROVIDER", "manual")
    if provider_name == "payme":
        return PaymeProvider()
    return ManualTestProvider()
