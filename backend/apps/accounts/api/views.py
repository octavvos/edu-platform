from django.conf import settings
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts import services
from apps.accounts.models import User
from apps.accounts.serializers import (
    CustomTokenObtainPairSerializer,
    OTPRequestSerializer,
    OTPVerifySerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.register_user(validated_data=serializer.validated_data)
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

        if purpose == "login" and not User.objects.filter(phone=phone).exists():
            return Response({"detail": "Bu raqam bilan ro'yxatdan o'tilmagan."}, status=status.HTTP_404_NOT_FOUND)

        otp = services.request_otp(phone=phone, purpose=purpose)
        payload = {"detail": "OTP kod yuborildi."}
        if settings.DEBUG:
            payload["code"] = otp.code  # faqat DEBUG rejimida test uchun
        return Response(payload, status=status.HTTP_200_OK)


class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, tokens = services.verify_otp(**serializer.validated_data)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({**tokens, "user": UserSerializer(user).data}, status=status.HTTP_200_OK)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AccountDeletionRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        services.request_account_deletion(user=request.user)
        return Response({"detail": "Akkauntni o'chirish so'rovi qabul qilindi (30 kun grace davri)."})
