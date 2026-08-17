"""
D-07: to'lov muvaffaqiyatli bo'lganda `payments` moduli `enrollment`ni
import qilmaydi — `payment_succeeded` hodisasini chiqaradi, shu yerda
unga obuna bo'linadi.
"""

from apps.core.events import subscribe

from . import services
from .models import Enrollment


@subscribe("payment_succeeded")
def on_payment_succeeded(*, user_id, course_id, **_):
    from apps.accounts.models import User
    from apps.courses.models import Course

    user = User.objects.filter(pk=user_id).first()
    course = Course.objects.filter(pk=course_id).first()
    if user and course:
        services.enroll_student(student=user, course=course, access_type=Enrollment.AccessType.PURCHASED)


@subscribe("order_refunded")
def on_order_refunded(*, user_id, **_):
    from apps.payments.models import Order

    order = Order.objects.filter(status=Order.Status.REFUNDED, user_id=user_id).order_by("-updated_at").first()
    if not order:
        return
    Enrollment.objects.filter(student_id=user_id, course_id=order.course_id).update(status=Enrollment.Status.CANCELLED)
