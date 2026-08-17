from django.contrib import admin

from .models import DripRule, Enrollment, Progress


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "status", "access_type", "progress_percent", "starts_at")
    list_filter = ("status", "access_type")
    search_fields = ("student__username", "course__title")


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "lesson", "status", "seconds_watched", "updated_at")
    list_filter = ("status",)


@admin.register(DripRule)
class DripRuleAdmin(admin.ModelAdmin):
    list_display = ("lesson", "rule_type", "unlock_at", "min_score_percent")
