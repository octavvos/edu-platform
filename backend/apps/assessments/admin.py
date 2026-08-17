from django.contrib import admin

from .models import Answer, Attempt, Choice, Question


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "lesson", "question_type")
    list_filter = ("question_type",)
    search_fields = ("text",)
    inlines = [ChoiceInline]


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "score", "total", "score_percent", "submitted_at")
    list_filter = ("submitted_at",)
    search_fields = ("user__username",)


admin.site.register(Answer)
