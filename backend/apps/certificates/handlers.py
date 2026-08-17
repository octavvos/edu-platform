"""D-07: `enrollments` moduli `course_completed` hodisasini chiqaradi,
bu yerda unga obuna bo'linadi — to'g'ridan-to'g'ri import yo'q."""

from apps.core.events import subscribe

from . import services


@subscribe("course_completed")
def on_course_completed(*, enrollment_id, **_):
    from apps.enrollments.models import Enrollment

    enrollment = Enrollment.objects.filter(pk=enrollment_id).first()
    if enrollment:
        services.issue_certificate(enrollment=enrollment)
