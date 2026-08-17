"""
TZ 5.1: barcha yozish (business logic) shu qatlam orqali — API view,
admin va Celery bir xil funksiyalarni chaqiradi.
"""

import logging

from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.events import emit

from .models import OTPCode, User

logger = logging.getLogger(__name__)


def send_otp_sms(phone: str, code: str) -> None:
    """
    I-02 (Eskiz.uz) stub. Haqiqiy SMS-shlyuz hisobi ulanmaguncha kodni
    logga yozadi. Production'da bu funksiya Eskiz.uz REST API'siga
    ulanadi — chaqiruvchi kod (services/API) o'zgarishsiz qoladi.
    """
    logger.info("[SMS STUB] OTP %s raqamiga yuborildi: %s", phone, code)


def register_user(*, validated_data: dict) -> User:
    user = User(**{k: v for k, v in validated_data.items() if k != "password"})
    user.set_password(validated_data["password"])
    user.save()

    if user.phone:
        otp = OTPCode.create_for_phone(user.phone, purpose=OTPCode.Purpose.REGISTER, user=user)
        send_otp_sms(user.phone, otp.code)

    emit("user_registered", user_id=str(user.id))
    return user


def request_otp(*, phone: str, purpose: str) -> OTPCode:
    user = User.objects.filter(phone=phone).first()
    otp = OTPCode.create_for_phone(phone, purpose=purpose, user=user)
    send_otp_sms(phone, otp.code)
    return otp


def verify_otp(*, phone: str, code: str, purpose: str) -> tuple[User, dict]:
    """Muvaffaqiyatli bo'lsa (user, tokens) qaytaradi; aks holda ValueError."""
    otp = (
        OTPCode.objects.filter(phone=phone, purpose=purpose, is_used=False)
        .order_by("-created_at")
        .first()
    )
    if not otp:
        raise ValueError("OTP kod topilmadi yoki muddati o'tgan.")

    otp.attempts += 1
    otp.save(update_fields=["attempts"])

    if not otp.is_valid(code):
        raise ValueError("OTP kod noto'g'ri yoki muddati o'tgan.")

    otp.is_used = True
    otp.save(update_fields=["is_used"])

    user = otp.user or User.objects.filter(phone=phone).first()
    if not user:
        raise ValueError("Foydalanuvchi topilmadi.")

    if purpose == OTPCode.Purpose.REGISTER and not user.is_phone_verified:
        user.is_phone_verified = True
        user.save(update_fields=["is_phone_verified"])
        emit("user_phone_verified", user_id=str(user.id))

    tokens = issue_tokens(user)
    return user, tokens


def issue_tokens(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


def request_account_deletion(*, user: User) -> User:
    """U-06: 30 kunlik grace davri, keyin anonimizatsiya."""
    user.status = User.Status.PENDING_DELETION
    user.deletion_requested_at = timezone.now()
    user.save(update_fields=["status", "deletion_requested_at"])
    return user
