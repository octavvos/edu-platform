import uuid

from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    N-01..N-05: MVP'da faqat in-app kanal ishlaydi (real vaqtda emas,
    REST orqali o'qiladi). Push (FCM)/Email/SMS uchun I-05/I-06/I-02
    hisoblari ulanmagan — `services.notify()` shu integratsiyalar
    ulanganda ham API o'zgarishisiz kengaytiriladi.
    """

    class NotificationType(models.TextChoices):
        LESSON_OPENED = "lesson_opened", "Yangi dars ochildi"
        DEADLINE_SOON = "deadline_soon", "Deadline yaqinlashdi"
        HOMEWORK_GRADED = "homework_graded", "Vazifa tekshirildi"
        NEW_COMMENT = "new_comment", "Yangi izoh/javob"
        PAYMENT_SUCCESS = "payment_success", "To'lov muvaffaqiyatli"
        CERTIFICATE_READY = "certificate_ready", "Sertifikat tayyor"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    type = models.CharField(max_length=30, choices=NotificationType.choices)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} <- {self.type}"
