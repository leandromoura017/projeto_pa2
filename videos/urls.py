from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed_view, name='feed'),
    path('publicar/', views.publish_video_view, name='video_publish'),
    path('video/<int:video_id>/', views.video_detail_view, name='video_detail'),
    path('video/<int:video_id>/comment/', views.add_video_comment_view, name='video_comment'),
    path('video/<int:video_id>/note/', views.save_video_note_view, name='video_note'),
    path('video/<int:video_id>/trust/', views.toggle_trust_vote_view, name='video_trust_vote'),
    path('<int:video_id>/curtir/', views.toggle_video_like_view, name='video_like'),
]
