from django.contrib import admin
from .models import Course, Lesson, Enrollment


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('order', 'title', 'video', 'duration_seconds')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'technology', 'instructor', 'level', 'estimated_minutes', 'is_published', 'created_at')
    list_filter = ('is_published', 'level', 'technology')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'video', 'duration_seconds')
    list_filter = ('course__technology', 'course')
    search_fields = ('title', 'content')
    ordering = ('course', 'order')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'completed_at', 'is_active')
    list_filter = ('is_active', 'course')
    search_fields = ('user__email', 'course__title')
