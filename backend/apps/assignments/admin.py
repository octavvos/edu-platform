from django.contrib import admin

from .models import Homework, Submission


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("lesson", "deadline", "max_score")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "homework", "status", "score", "is_late", "submitted_at")
    list_filter = ("status", "is_late")
    search_fields = ("student__username",)
