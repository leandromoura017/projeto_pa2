from django.contrib import admin
from .models import Course, Lesson, Enrollment, LessonProgress, Challenge, ChallengeAttempt, Certificate


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


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'lesson__course')
    search_fields = ('user__email', 'lesson__title')


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'correct_option', 'expected_code_keyword', 'points', 'created_at')
    search_fields = ('title', 'question_text', 'lesson__title')
    list_filter = ('correct_option', 'lesson__course')


@admin.register(ChallengeAttempt)
class ChallengeAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'selected_option', 'is_correct', 'attempted_at')
    list_filter = ('is_correct', 'challenge__lesson__course')
    search_fields = ('user__email', 'challenge__title', 'submitted_code')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('validation_code', 'user', 'course', 'issued_at')
    list_filter = ('course', 'issued_at')
    search_fields = ('validation_code', 'user__email', 'course__title')

