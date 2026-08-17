import logging

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import OTPCode, User
from .serializers import (
    CustomTokenObtainPairSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    RegisterSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


def _send_otp_sms(phone, code):
    """MVP stub: SMS gateway o'rniga log/console orqali yuboriladi."""
    logger.info("OTP kod %s raqamiga yuborildi: %s", phone, code)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if user.phone:
            otp = OTPCode.create_for_phone(user.phone, purpose=OTPCode.Purpose.REGISTER, user=user)
            _send_otp_sms(user.phone, otp.code)

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class OTPRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]
        purpose = serializer.validated_data["purpose"]

        user = User.objects.filter(phone=phone).first()
        if purpose == OTPCode.Purpose.LOGIN and not user:
            return Response({"detail": "Bu raqam bilan ro'yxatdan o'tilmagan."}, status=status.HTTP_404_NOT_FOUND)

        otp = OTPCode.create_for_phone(phone, purpose=purpose, user=user)
        _send_otp_sms(phone, otp.code)

        payload = {"detail": "OTP kod yuborildi."}
        from django.conf import settings as dj_settings
        if dj_settings.DEBUG:
            payload["code"] = otp.code  # faqat DEBUG rejimida test uchun
        return Response(payload, status=status.HTTP_200_OK)


class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["code"]
        purpose = serializer.validated_data["purpose"]

        otp = OTPCode.objects.filter(phone=phone, purpose=purpose, is_used=False).order_by("-created_at").first()
        if not otp or not otp.is_valid(code):
            return Response({"detail": "OTP kod noto'g'ri yoki muddati o'tgan."}, status=status.HTTP_400_BAD_REQUEST)

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        user = otp.user or User.objects.filter(phone=phone).first()
        if not user:
            return Response({"detail": "Foydalanuvchi topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if purpose == OTPCode.Purpose.REGISTER:
            user.is_phone_verified = True
            user.save(update_fields=["is_phone_verified"])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
