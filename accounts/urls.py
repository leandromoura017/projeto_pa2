from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('profiles/', views.profile_search_view, name='profile_search'),
    path('profiles/<int:user_id>/', views.public_profile_view, name='public_profile'),
    path('dms/', views.dm_inbox_view, name='dm_inbox'),
    path('dms/batch/', views.dm_batch_action_view, name='dm_batch_action'),
    path('dms/<int:user_id>/', views.dm_thread_view, name='dm_thread'),
    path('dms/<int:user_id>/delete/', views.dm_delete_thread_view, name='dm_delete_thread'),
    path('dms/<int:user_id>/mark-read/', views.dm_mark_thread_read_view, name='dm_mark_thread_read'),
    path('dms/message/<int:message_id>/delete/', views.dm_delete_message_view, name='dm_delete_message'),
    path('notifications/', views.notification_list_view, name='notifications'),
    path('notifications/batch/', views.notification_batch_action_view, name='notification_batch_action'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read_view, name='notification_read'),
    path('notifications/<int:notification_id>/delete/', views.notification_delete_view, name='notification_delete'),
    path('notifications/read-all/', views.mark_all_notifications_read_view, name='notifications_read_all'),
    path('tam/', views.tam_evaluation_view, name='tam_evaluation'),
    path('avaliacao-tam/', views.tam_evaluation_view, name='tam_evaluation_alias'),
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard_alias'),
    path('delete/', views.account_delete_view, name='account_delete'),
    
    # Password Reset
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]
