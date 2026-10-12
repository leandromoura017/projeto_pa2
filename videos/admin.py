from django.contrib import admin
from .models import Technology, Video, VideoLike


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'technology', 'author', 'duration_seconds', 'views_count', 'is_published', 'created_at')
    list_filter = ('technology', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'author__email')
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(VideoLike)
class VideoLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'created_at')
    list_filter = ('created_at', 'video__technology')
    search_fields = ('user__email', 'video__title')
