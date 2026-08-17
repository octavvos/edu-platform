from django.db import transaction
from django.utils import timezone

from apps.core.events import emit

from .models import Answer, Attempt, Choice, Question

PASSING_SCORE_PERCENT = 60


@transaction.atomic
def grade_quiz(*, user, lesson, answers: dict) -> Attempt:
    """
    `answers`: {question_id: choice_id} (single/true_false) yoki
    {question_id: [choice_id, ...]} (multiple) yoki {question_id: "matn"} (short_text).

    T-01..T-07: natija darhol hisoblanadi, Attempt+Answer sifatida
    saqlanadi (urinishlar tarixi uchun), `quiz_submitted` hodisasi
    chiqariladi — enrollment moduli shunga obuna bo'lib progress'ni
    yangilaydi (to'g'ridan-to'g'ri import qilinmaydi, D-07).
    """
    questions = list(lesson.questions.prefetch_related("choices"))
    attempt = Attempt.objects.create(user=user, lesson=lesson, total=len(questions))

    correct_count = 0
    for question in questions:
        submitted = answers.get(str(question.id))
        is_correct = _check_answer(question, submitted)
        if is_correct:
            correct_count += 1

        answer = Answer.objects.create(
            attempt=attempt, question=question,
            text_answer=str(submitted) if question.question_type == Question.QuestionType.SHORT_TEXT and submitted else "",
            is_correct=is_correct,
        )
        if question.question_type in (Question.QuestionType.SINGLE, Question.QuestionType.TRUE_FALSE) and submitted:
            answer.selected_choices.set(Choice.objects.filter(pk=submitted))
        elif question.question_type == Question.QuestionType.MULTIPLE and submitted:
            answer.selected_choices.set(Choice.objects.filter(pk__in=submitted))

    attempt.score = correct_count
    attempt.score_percent = round(correct_count / len(questions) * 100) if questions else 0
    attempt.submitted_at = timezone.now()
    attempt.save(update_fields=["score", "score_percent", "submitted_at"])

    emit(
        "quiz_submitted",
        user_id=str(user.id), lesson_id=str(lesson.id),
        score_percent=attempt.score_percent, passed=attempt.score_percent >= PASSING_SCORE_PERCENT,
    )
    return attempt


def _check_answer(question: Question, submitted) -> bool:
    if submitted is None:
        return False

    if question.question_type in (Question.QuestionType.SINGLE, Question.QuestionType.TRUE_FALSE):
        correct = question.choices.filter(is_correct=True).first()
        return bool(correct) and str(submitted) == str(correct.id)

    if question.question_type == Question.QuestionType.MULTIPLE:
        correct_ids = set(str(c.id) for c in question.choices.filter(is_correct=True))
        submitted_ids = set(str(c) for c in (submitted if isinstance(submitted, list) else []))
        return correct_ids == submitted_ids

    if question.question_type == Question.QuestionType.SHORT_TEXT:
        import re

        pattern = question.expected_answer_pattern
        if not pattern:
            return False
        return bool(re.fullmatch(pattern, str(submitted).strip(), re.IGNORECASE))

    return False


def correct_choice_map(lesson) -> dict:
    result = {}
    for question in lesson.questions.prefetch_related("choices"):
        correct = question.choices.filter(is_correct=True).first()
        result[str(question.id)] = str(correct.id) if correct else None
    return result
