from .models import Review


def create_review(*, user, course, rating: int, comment: str = "") -> Review:
    """K-08: faqat kursga yozilgan (sotib olgan) foydalanuvchilar sharh qoldira oladi."""
    from apps.enrollments.models import Enrollment

    is_enrolled = Enrollment.objects.filter(student=user, course=course).exists()
    if not is_enrolled:
        raise ValueError("Faqat kursga yozilganlar sharh qoldira oladi.")

    review, _ = Review.objects.update_or_create(
        course=course, user=user,
        defaults={"rating": rating, "comment": comment, "is_published": False},
    )
    return review
