import uuid

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments import services
from apps.payments.models import LedgerEntry, Order, Promo
from apps.payments.serializers import LedgerEntrySerializer, OrderSerializer, PromoSerializer
from apps.rbac.services import has_permission


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "course"]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or has_permission(user, "payment.view_any"):
            return Order.objects.select_related("course", "user")
        return Order.objects.filter(user=user).select_related("course")

    def create(self, request, *args, **kwargs):
        course_id = request.data.get("course")
        promo_code = request.data.get("promo_code")
        idempotency_key = request.headers.get("Idempotency-Key") or str(uuid.uuid4())

        from apps.courses.models import Course

        course = Course.objects.filter(pk=course_id).first()
        if not course:
            return Response({"detail": "Kurs topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        promo = Promo.objects.filter(code=promo_code).first() if promo_code else None

        order = services.create_order(
            user=request.user, course=course, idempotency_key=idempotency_key, promo=promo,
        )
        checkout = services.start_checkout(order=order)
        order.refresh_from_db()
        return Response(
            {"order": OrderSerializer(order).data, "checkout": checkout},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def refund(self, request, pk=None):
        order = self.get_object()
        order = services.refund_order(order=order, admin_user=request.user)
        return Response(OrderSerializer(order).data)


class PromoValidateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = request.data.get("code", "")
        promo = Promo.objects.filter(code=code).first()
        if not promo:
            return Response({"valid": False, "detail": "Promokod topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"valid": True, **PromoSerializer(promo).data})


class LedgerViewSet(viewsets.ReadOnlyModelViewSet):
    """AD-04: moliyaviy operatsiyalar — faqat admin."""

    serializer_class = LedgerEntrySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = LedgerEntry.objects.all()
    filterset_fields = ["account", "ref_type"]


class PaymeWebhookView(APIView):
    """
    P-03/P-04: webhook orqali to'lov holatini tasdiqlash.

    I-01: haqiqiy Payme integratsiyasi ulanmagan — bu endpoint hozircha
    faqat 501 qaytaradi. Merchant kalitlari kelganda `providers.PaymeProvider`
    to'ldiriladi va shu view HMAC tekshiruvidan so'ng
    `services.mark_order_paid()` ni chaqiradi.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response(
            {"detail": "Payme integratsiyasi hali ulanmagan (merchant kalitlari kerak)."},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
