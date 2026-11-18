"""
URL configuration for CodeView project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from accounts.views import profile_view, profile_edit_view, tam_evaluation_view, admin_dashboard_view
from videos.views import feed_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('painel-admin/', admin_dashboard_view, name='admin_dashboard'),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'img/favicon.ico', permanent=True)),
    path('accounts/', include('accounts.urls')),
    path('avaliacao-tam/', tam_evaluation_view, name='tam_evaluation_root'),
    path('', feed_view, name='home'),
    path('feed/', include('videos.urls')),
    path('courses/', include('courses.urls')),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)
