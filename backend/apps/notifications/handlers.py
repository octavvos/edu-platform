from apps.core.events import subscribe

from .models import Notification
from .services import notify


@subscribe("payment_succeeded")
def on_payment_succeeded(*, user_id, course_id, **_):
    from apps.accounts.models import User
    from apps.courses.models import Course

    user = User.objects.filter(pk=user_id).first()
    course = Course.objects.filter(pk=course_id).first()
    if user and course:
        notify(
            user=user, type=Notification.NotificationType.PAYMENT_SUCCESS,
            title="To'lov muvaffaqiyatli", body=f"\"{course.title}\" kursiga yozildingiz.",
        )


@subscribe("certificate_issued")
def on_certificate_issued(*, user_id, **_):
    from apps.accounts.models import User

    user = User.objects.filter(pk=user_id).first()
    if user:
        notify(
            user=user, type=Notification.NotificationType.CERTIFICATE_READY,
            title="Sertifikatingiz tayyor", body="Kursni tugatganingiz uchun tabriklaymiz!",
        )


@subscribe("homework_graded")
def on_homework_graded(*, student_id, score, accepted, **_):
    from apps.accounts.models import User

    user = User.objects.filter(pk=student_id).first()
    if user:
        status_text = "qabul qilindi" if accepted else "qayta ishlashga qaytarildi"
        notify(
            user=user, type=Notification.NotificationType.HOMEWORK_GRADED,
            title="Uy vazifangiz tekshirildi", body=f"Ball: {score}. Holat: {status_text}.",
        )
