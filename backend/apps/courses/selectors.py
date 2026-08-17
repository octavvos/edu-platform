"""TZ 5.1: o'qish operatsiyalari (queryset filtrlash) shu qatlamda."""

from django.db.models import Q, QuerySet


def visible_lessons_for_user(queryset: QuerySet, user) -> QuerySet:
    """Bepul preview / kurs egasi / faol enrollment / admin — R-05 (avtomatik filtrlash)."""
    if not user.is_authenticated:
        return queryset.filter(is_free_preview=True)
    if user.is_admin:
        return queryset

    from apps.enrollments.models import Enrollment

    enrolled_course_ids = Enrollment.objects.filter(
        student=user, status=Enrollment.Status.ACTIVE
    ).values_list("course_id", flat=True)

    return queryset.filter(
        Q(is_free_preview=True)
        | Q(module__course__teacher=user)
        | Q(module__course_id__in=enrolled_course_ids)
    )
