from apps.core.events import emit

from .models import Course


def submit_for_moderation(*, course: Course) -> Course:
    """C-02: qoralama -> moderatsiyada."""
    course.status = Course.Status.MODERATION
    course.save(update_fields=["status"])
    return course


def publish_course(*, course: Course, moderator=None) -> Course:
    """AD-02: admin tasdiqlashi bilan nashr etiladi."""
    course.status = Course.Status.PUBLISHED
    course.save(update_fields=["status"])
    emit("course_published", course_id=str(course.id), moderator_id=str(moderator.id) if moderator else None)
    return course


def reject_course(*, course: Course, reason: str = "") -> Course:
    course.status = Course.Status.REJECTED
    course.save(update_fields=["status"])
    return course
