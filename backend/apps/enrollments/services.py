from django.utils import timezone

from apps.core.events import emit

from .models import Enrollment, Progress


def enroll_student(*, student, course, access_type=Enrollment.AccessType.FREE) -> Enrollment:
    enrollment, created = Enrollment.objects.get_or_create(
        student=student, course=course, defaults={"access_type": access_type},
    )
    if created:
        emit("enrollment_created", enrollment_id=str(enrollment.id))
    return enrollment


def mark_lesson_progress(*, enrollment: Enrollment, lesson, status: str, seconds_watched: int = 0,
                          last_position: int = 0) -> Progress:
    """G-01/G-03: dars progressini yozadi va Enrollment.progress_percent'ni qayta hisoblaydi."""
    progress, _ = Progress.objects.update_or_create(
        enrollment=enrollment, lesson=lesson,
        defaults={
            "status": status,
            "seconds_watched": seconds_watched,
            "last_position": last_position,
            "completed_at": timezone.now() if status == Progress.Status.COMPLETED else None,
        },
    )
    recalculate_enrollment_progress(enrollment=enrollment)
    return progress


def recalculate_enrollment_progress(*, enrollment: Enrollment) -> Enrollment:
    """G-03: kurs strukturasi o'zgarganda ham qayta hisoblanadi (required darslar bo'yicha)."""
    from apps.courses.models import Lesson

    required_lesson_ids = Lesson.objects.filter(
        module__course=enrollment.course, is_required=True,
    ).values_list("id", flat=True)
    total = required_lesson_ids.count() or 1

    completed = Progress.objects.filter(
        enrollment=enrollment, lesson_id__in=required_lesson_ids, status=Progress.Status.COMPLETED,
    ).count()

    enrollment.completed_lessons_count = completed
    enrollment.progress_percent = min(100, round(completed / total * 100))

    if enrollment.progress_percent >= 100 and enrollment.status == Enrollment.Status.ACTIVE:
        enrollment.status = Enrollment.Status.COMPLETED
        enrollment.completed_at = timezone.now()
        emit("course_completed", enrollment_id=str(enrollment.id))

    enrollment.save(update_fields=["progress_percent", "completed_lessons_count", "status", "completed_at"])
    return enrollment
