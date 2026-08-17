from django.utils import timezone

from apps.core.events import emit

from .models import Homework, Submission


def submit_homework(*, student, homework: Homework, **fields) -> Submission:
    is_late = bool(homework.deadline and timezone.now() > homework.deadline)
    submission = Submission.objects.create(
        homework=homework, student=student, is_late=is_late, **fields,
    )
    emit("homework_submitted", submission_id=str(submission.id))
    return submission


def grade_submission(*, submission: Submission, mentor, score: int, feedback: str, status: str) -> Submission:
    """H-04: mentor izohi va ball (0-100) qo'yishi."""
    submission.mentor = mentor
    submission.score = score
    submission.feedback = feedback
    submission.status = status
    submission.reviewed_at = timezone.now()
    submission.save(update_fields=["mentor", "score", "feedback", "status", "reviewed_at"])

    emit(
        "homework_graded",
        submission_id=str(submission.id), student_id=str(submission.student_id),
        score=score, accepted=(status == Submission.Status.ACCEPTED),
    )
    return submission
