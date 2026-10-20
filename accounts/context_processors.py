def notifications_context(request):
    """
    Context processor para disponibilizar o contador do sininho de alertas
    e as últimas notificações em todas as páginas da aplicação (Onda 5 - #23).
    """
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(is_read=False).count()
        recent_notifications = request.user.notifications.all()[:5]
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent_notifications,
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': [],
    }

