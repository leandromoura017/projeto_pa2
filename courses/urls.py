from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list_view, name='course_list'),
    path('<slug:slug>/', views.course_detail_view, name='course_detail'),
    path('<slug:slug>/enroll/', views.enroll_course_view, name='course_enroll'),
    path('<slug:slug>/unenroll/', views.unenroll_course_view, name='course_unenroll'),
    path('aulas/<int:lesson_id>/desafio/', views.lesson_challenge_view, name='lesson_challenge'),
]
