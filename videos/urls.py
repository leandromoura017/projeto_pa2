from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('publicar/', views.publish_video_view, name='video_publish'),
    path('<int:video_id>/curtir/', views.toggle_video_like_view, name='video_like'),
]
