from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list_view, name='course_list'),
    path('certificados/<str:validation_code>/', views.certificate_detail_view, name='certificate_detail'),
    path('certificados/<str:validation_code>/pdf/', views.download_certificate_pdf_view, name='certificate_pdf'),
    path('certificados/<str:validation_code>/qr/', views.certificate_qr_code_view, name='certificate_qr'),
    path('aulas/<int:lesson_id>/desafio/', views.lesson_challenge_view, name='lesson_challenge'),
    path('aulas/<int:lesson_id>/concluir/', views.complete_lesson_view, name='lesson_complete'),
    path('meus-cursos/', views.my_courses_view, name='my_courses'),
    path('cadastrar/', views.course_create_view, name='course_create'),
    path('<slug:slug>/gerenciar/', views.course_manage_view, name='course_manage'),
    path('<slug:slug>/editar/', views.course_manage_view, name='course_edit'),
    path('<slug:slug>/aulas/adicionar/', views.lesson_create_view, name='lesson_create'),
    path('<slug:slug>/aulas/<int:lesson_id>/editar/', views.lesson_edit_view, name='lesson_edit'),
    path('<slug:slug>/aulas/<int:lesson_id>/excluir/', views.lesson_delete_view, name='lesson_delete'),
    path('<slug:slug>/aulas/<int:lesson_id>/reordenar/<str:direction>/', views.lesson_reorder_view, name='lesson_reorder'),
    path('<slug:slug>/aulas/<int:lesson_id>/desafio/gerenciar/', views.challenge_manage_view, name='challenge_manage'),
    path('<slug:slug>/', views.course_detail_view, name='course_detail'),
    path('<slug:slug>/enroll/', views.enroll_course_view, name='course_enroll'),
    path('<slug:slug>/unenroll/', views.unenroll_course_view, name='course_unenroll'),
    path('<slug:slug>/certificado/emitir/', views.issue_certificate_view, name='issue_certificate'),
]
