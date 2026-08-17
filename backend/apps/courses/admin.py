from django.contrib import admin

from .models import Course, Lesson, Module, VideoAsset


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "category", "level", "price", "status", "created_at")
    list_filter = ("level", "status", "category")
    search_fields = ("title", "description", "teacher__username")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "content_type", "duration_minutes", "is_required", "is_free_preview")
    list_filter = ("content_type", "is_required", "is_free_preview")


@admin.register(VideoAsset)
class VideoAssetAdmin(admin.ModelAdmin):
    list_display = ("lesson", "provider", "status", "duration_seconds")
    list_filter = ("provider", "status")
