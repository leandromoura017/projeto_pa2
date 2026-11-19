import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import JsonResponse
from django.urls import reverse
from .forms import SignUpForm, LoginForm, ProfileEditForm
from .models import User, Profile, DirectMessage, Notification, TAMEvaluation


def _build_portfolio_context(target_user, request=None):
    """
    Constrói os indicadores e registros verificáveis do Portfólio Vivo de um usuário
    incluindo o Medidor de Conhecimento Técnico (Onda 8 - #35) e URLs de compartilhamento (Onda 8 - #32).
    """
    from courses.models import Enrollment, ChallengeAttempt, Certificate, LessonProgress
    from videos.models import Technology

    profile, _ = Profile.objects.get_or_create(user=target_user)
    solved_attempts = ChallengeAttempt.objects.filter(
        user=target_user,
        is_correct=True
    ).select_related('challenge', 'challenge__lesson', 'challenge__lesson__course', 'challenge__lesson__course__technology').order_by('-attempted_at')

    certificates = Certificate.objects.filter(
        user=target_user
    ).select_related('course', 'course__technology').order_by('-issued_at')

    enrollments = Enrollment.objects.filter(
        user=target_user,
        is_active=True
    ).select_related('course', 'course__technology').order_by('-enrolled_at')

    enrollment_cards = []
    for enr in enrollments:
        comp, tot, pct = enr.course.get_user_progress(target_user)
        enrollment_cards.append({
            'enrollment': enr,
            'course': enr.course,
            'completed_count': comp,
            'total_count': tot,
            'progress_pct': pct,
        })

    lessons_completed_count = LessonProgress.objects.filter(
        user=target_user,
        is_completed=True
    ).count()

    published_videos = target_user.videos.filter(is_published=True).select_related('technology').order_by('-created_at')

    # Medidor de Conhecimento Técnico (Onda 8 - #35)
    total_points = sum(a.challenge.points for a in solved_attempts if a.challenge and a.challenge.points)

    tech_stats = []
    all_technologies = Technology.objects.filter(is_active=True).order_by('name')
    for tech in all_technologies:
        tech_solved = solved_attempts.filter(challenge__lesson__course__technology=tech).count()
        tech_certs = certificates.filter(course__technology=tech).count()
        tech_videos = published_videos.filter(technology=tech).count()

        # Cálculo ponderado de domínio prático (0 a 100%)
        raw_score = (tech_solved * 30) + (tech_certs * 50) + (tech_videos * 20)
        percentage = min(100, raw_score)

        if percentage >= 80:
            level_label = "Avançado / Especialista"
            badge_color = "emerald"
        elif percentage >= 40:
            level_label = "Intermediário / Praticante"
            badge_color = "cyan"
        elif percentage > 0:
            level_label = "Iniciante / Em Formação"
            badge_color = "blue"
        else:
            level_label = "Não Iniciado"
            badge_color = "gray"

        tech_stats.append({
            'tech': tech,
            'solved_count': tech_solved,
            'certs_count': tech_certs,
            'videos_count': tech_videos,
            'percentage': percentage,
            'level_label': level_label,
            'badge_color': badge_color,
            'has_activity': percentage > 0,
        })

    # Maturidade global de conhecimento prático
    active_techs_count = sum(1 for t in tech_stats if t['has_activity'])
    overall_points = total_points + (certificates.count() * 50) + (lessons_completed_count * 10) + (published_videos.count() * 15)

    if overall_points >= 200 or certificates.count() >= 2:
        overall_rank = "Senior Tech Lead • Especialista"
        overall_pct = min(100, 75 + min(25, (overall_points - 200) // 10))
        rank_badge_color = "purple"
    elif overall_points >= 100 or certificates.count() >= 1:
        overall_rank = "Pleno Developer • Autônomo"
        overall_pct = min(74, 50 + ((overall_points - 100) // 4))
        rank_badge_color = "cyan"
    elif overall_points >= 30 or solved_attempts.count() >= 1:
        overall_rank = "Junior Developer • Em Ascensão"
        overall_pct = min(49, 25 + ((overall_points - 30) // 3))
        rank_badge_color = "blue"
    else:
        overall_rank = "Estudante Praticante • Iniciante"
        overall_pct = 15
        rank_badge_color = "emerald"

    # Link de compartilhamento público (Onda 8 - #32)
    if request:
        absolute_profile_url = request.build_absolute_uri(reverse('public_profile', kwargs={'user_id': target_user.id}))
    else:
        absolute_profile_url = f"/accounts/profiles/{target_user.id}/"

    return {
        'profile': profile,
        'target_user': target_user,
        'solved_attempts': solved_attempts,
        'challenges_solved_count': solved_attempts.count(),
        'certificates': certificates,
        'certificates_count': certificates.count(),
        'enrollment_cards': enrollment_cards,
        'lessons_completed_count': lessons_completed_count,
        'published_videos': published_videos,
        'videos_published_count': published_videos.count(),
        'total_points': total_points,
        'tech_stats': tech_stats,
        'active_techs_count': active_techs_count,
        'overall_points': overall_points,
        'overall_pct': overall_pct,
        'overall_rank': overall_rank,
        'rank_badge_color': rank_badge_color,
        'absolute_profile_url': absolute_profile_url,
    }


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('feed')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(request=request)
            login(request, user)
            messages.success(request, f"Conta criada com sucesso! Seja bem-vindo ao CodeView, {user.first_name}!")
            return redirect('feed')
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')

    next_url = request.GET.get('next', 'feed')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=email, password=password)
            if user is None:
                user = authenticate(request, email=email, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Olá novamente, {user.first_name or user.email}!")
                    return redirect(next_url if next_url else 'feed')
                else:
                    form.add_error(None, "Esta conta está inativa.")
            else:
                form.add_error(None, "E-mail ou senha inválidos.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "Você encerrou sua sessão com segurança.")
    return redirect('login')


def terms_view(request):
    return render(request, 'legal/terms.html')


def privacy_view(request):
    return render(request, 'legal/privacy.html')


def feed_view(request):
    """Fallback defensivo: delega para a view oficial do feed de vídeos."""
    from videos.views import feed_view as official_feed_view
    return official_feed_view(request)


@login_required
def profile_view(request):
    context = _build_portfolio_context(request.user, request=request)
    context['user'] = request.user
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            profile.bio = form.cleaned_data['bio']
            profile.github_url = form.cleaned_data['github_url']
            profile.linkedin_url = form.cleaned_data['linkedin_url']

            if 'avatar' in request.FILES:
                profile.avatar = form.cleaned_data['avatar']

            profile.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('profile')
    else:
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': profile.bio,
            'github_url': profile.github_url,
            'linkedin_url': profile.linkedin_url,
        }
        form = ProfileEditForm(initial=initial_data)

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'profile': profile,
    })


@login_required
def account_delete_view(request):
    """
    Encerramento definitivo de conta e exclusão de dados pessoais (Onda 8 - #33).
    Conformidade com a LGPD (Lei Geral de Proteção de Dados - Artigo 18 - Direito à Eliminação).
    """
    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        confirm_keyword = request.POST.get('confirm_keyword', '').strip().upper()

        valid = False
        if password and request.user.check_password(password):
            valid = True
        elif confirm_keyword in ['DELETAR', 'EXCLUIR']:
            valid = True
        elif not request.user.has_usable_password() and confirm_keyword in ['DELETAR', 'EXCLUIR']:
            valid = True

        if not valid:
            messages.error(request, "Para encerrar sua conta conforme a LGPD, confirme sua senha ou digite a palavra 'DELETAR'.")
            return redirect('profile_edit')

        user = request.user
        user_email = user.email
        logout(request)
        user.delete()
        messages.success(request, f"Sua conta ({user_email}) e todos os seus dados pessoais foram permanentemente eliminados em conformidade com a LGPD.")
        return redirect('login')

    return render(request, 'accounts/account_delete_confirm.html', {'user': request.user})


@login_required
def profile_search_view(request):
    """
    Busca de Perfis / Portfólios Vivos de alunos e mentores na plataforma (Onda 4 - #16).
    Permite filtrar por palavra-chave (nome, bio, especialidade, e-mail) e tipo (mentores).
    """
    query = request.GET.get('q', '').strip()
    role = request.GET.get('role', '').strip()

    users_qs = User.objects.filter(is_active=True).select_related('profile').annotate(
        solved_count=Count('challenge_attempts', filter=Q(challenge_attempts__is_correct=True), distinct=True),
        certs_count=Count('certificates', distinct=True),
    ).order_by('-certs_count', '-solved_count', 'first_name')

    if role == 'mentor':
        users_qs = users_qs.filter(profile__is_mentor=True)

    if query:
        users_qs = users_qs.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(profile__bio__icontains=query) |
            Q(profile__specialties__icontains=query)
        )

    return render(request, 'accounts/profile_search.html', {
        'profiles_users': users_qs,
        'query': query,
        'current_role': role,
    })


@login_required
def public_profile_view(request, user_id):
    """
    Visualização pública do Portfólio Vivo de qualquer usuário/mentor da plataforma (Onda 4).
    """
    target_user = get_object_or_404(User, id=user_id, is_active=True)
    context = _build_portfolio_context(target_user, request=request)
    return render(request, 'accounts/profile_public.html', context)


@login_required
def dm_inbox_view(request):
    """
    Aba de DMs (Mensagens Diretas) para conversas com mentores e colegas (Onda 4 - #19).
    """
    sent_to_ids = DirectMessage.objects.filter(sender=request.user).values_list('recipient_id', flat=True)
    received_from_ids = DirectMessage.objects.filter(recipient=request.user).values_list('sender_id', flat=True)
    partner_ids = set(sent_to_ids) | set(received_from_ids)

    conversations = []
    if partner_ids:
        partners = User.objects.filter(id__in=partner_ids, is_active=True).select_related('profile')
        for partner in partners:
            last_msg = DirectMessage.objects.filter(
                Q(sender=request.user, recipient=partner) | Q(sender=partner, recipient=request.user)
            ).order_by('-created_at').first()
            unread_count = DirectMessage.objects.filter(
                sender=partner,
                recipient=request.user,
                is_read=False
            ).count()
            conversations.append({
                'partner': partner,
                'last_message': last_msg,
                'unread_count': unread_count,
            })
        conversations.sort(key=lambda c: c['last_message'].created_at if c['last_message'] else c['partner'].date_joined, reverse=True)

    mentors = User.objects.filter(
        is_active=True,
        profile__is_mentor=True
    ).exclude(id=request.user.id).select_related('profile')

    return render(request, 'accounts/dm_inbox.html', {
        'conversations': conversations,
        'mentors': mentors,
    })


@login_required
def dm_thread_view(request, user_id):
    """
    Tela de conversa direta (chat/DM) com um mentor ou usuário específico (Onda 4 - #19).
    Dispara notificação para o destinatário da mensagem (Onda 6 - #26).
    """
    other_user = get_object_or_404(User.objects.select_related('profile'), id=user_id, is_active=True)

    if other_user.id == request.user.id:
        messages.info(request, "Selecione um mentor ou outro usuário para conversar por DM.")
        return redirect('dm_inbox')

    # Marca mensagens recebidas desse remetente como lidas
    DirectMessage.objects.filter(
        sender=other_user,
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            msg = DirectMessage.objects.create(
                sender=request.user,
                recipient=other_user,
                content=content
            )

            # Notificação para o destinatário da mensagem (Onda 6 - #26)
            sender_name = request.user.first_name or request.user.username
            preview_text = content[:80] + ('...' if len(content) > 80 else '')
            Notification.objects.create(
                user=other_user,
                title=f"💬 Nova mensagem de {sender_name}",
                message=preview_text,
                link=reverse('dm_thread', kwargs={'user_id': request.user.id}),
                icon='💬'
            )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message_id': msg.id,
                    'content': msg.content,
                    'created_at': msg.created_at.strftime('%H:%M'),
                })
            return redirect('dm_thread', user_id=other_user.id)
        else:
            messages.error(request, "Digite uma mensagem antes de enviar.")

    thread_messages = DirectMessage.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).select_related('sender', 'recipient').order_by('created_at')

    return render(request, 'accounts/dm_thread.html', {
        'other_user': other_user,
        'thread_messages': thread_messages,
    })


@login_required
def dm_delete_message_view(request, message_id):
    """
    Exclui uma mensagem individual (DM) pertencente ao usuário atual (como remetente ou destinatário).
    """
    msg = get_object_or_404(
        DirectMessage.objects.filter(Q(sender=request.user) | Q(recipient=request.user)),
        id=message_id
    )
    partner_id = msg.recipient_id if msg.sender_id == request.user.id else msg.sender_id
    msg.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'status': 'success', 'message_id': message_id})

    messages.success(request, "Mensagem excluída com sucesso.")
    return redirect('dm_thread', user_id=partner_id)


@login_required
def dm_batch_action_view(request):
    """
    Executa ações em lote em mensagens diretas selecionadas:
    - delete: exclui as mensagens selecionadas
    - mark_read: marca as mensagens recebidas selecionadas como lidas
    - mark_unread: marca as mensagens recebidas selecionadas como não lidas
    """
    if request.method != 'POST':
        return redirect('dm_inbox')

    action = request.POST.get('action')
    message_ids = request.POST.getlist('message_ids')
    partner_id = request.POST.get('partner_id')

    if not message_ids and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            action = data.get('action', action)
            message_ids = data.get('message_ids', [])
            partner_id = data.get('partner_id', partner_id)
        except Exception:
            pass

    if not message_ids:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'status': 'error', 'message': 'Nenhuma mensagem selecionada.'}, status=400)
        messages.warning(request, "Nenhuma mensagem foi selecionada.")
        if partner_id:
            return redirect('dm_thread', user_id=partner_id)
        return redirect('dm_inbox')

    user_messages = DirectMessage.objects.filter(
        id__in=message_ids
    ).filter(Q(sender=request.user) | Q(recipient=request.user))

    count = user_messages.count()

    if action == 'delete':
        user_messages.delete()
        msg_feedback = f"{count} mensagem(ns) excluída(s) com sucesso."
    elif action == 'mark_read':
        received = user_messages.filter(recipient=request.user)
        updated = received.update(is_read=True)
        msg_feedback = f"{updated} mensagem(ns) marcada(s) como lida(s)."
    elif action == 'mark_unread':
        received = user_messages.filter(recipient=request.user)
        updated = received.update(is_read=False)
        msg_feedback = f"{updated} mensagem(ns) marcada(s) como não lida(s)."
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'status': 'error', 'message': 'Ação inválida.'}, status=400)
        messages.error(request, "Ação inválida.")
        if partner_id:
            return redirect('dm_thread', user_id=partner_id)
        return redirect('dm_inbox')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'status': 'success', 'message': msg_feedback, 'count': count, 'action': action})

    messages.success(request, msg_feedback)
    if partner_id:
        return redirect('dm_thread', user_id=partner_id)
    return redirect('dm_inbox')


@login_required
def dm_delete_thread_view(request, user_id):
    """
    Exclui todo o histórico de mensagens entre o usuário logado e o usuário parceiro.
    """
    if request.method != 'POST':
        return redirect('dm_inbox')

    partner = get_object_or_404(User, id=user_id)
    DirectMessage.objects.filter(
        Q(sender=request.user, recipient=partner) |
        Q(sender=partner, recipient=request.user)
    ).delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'status': 'success', 'partner_id': user_id})

    messages.success(request, f"Toda a conversa com {partner.first_name or partner.username} foi excluída.")
    return redirect('dm_inbox')


@login_required
def dm_mark_thread_read_view(request, user_id):
    """
    Marca todas as mensagens recebidas de um determinado usuário como lidas.
    """
    if request.method != 'POST':
        return redirect('dm_inbox')

    partner = get_object_or_404(User, id=user_id)
    updated = DirectMessage.objects.filter(
        sender=partner,
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'status': 'success', 'partner_id': user_id, 'updated': updated})

    messages.success(request, f"Mensagens de {partner.first_name or partner.username} marcadas como lidas.")
    return redirect('dm_inbox')


@login_required
def notification_list_view(request):
    """
    Central de Notificações / Alertas (sininho) de novas publicações e avisos (Onda 5 - #23).
    """
    notifications = request.user.notifications.all()
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'accounts/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def mark_notification_read_view(request, notification_id):
    """
    Marca uma notificação individual como lida e redireciona para o link associado se houver.
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()

    unread_count = request.user.notifications.filter(is_read=False).count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'notification_id': notification.id,
            'unread_count': unread_count,
        })

    if notification.link:
        return redirect(notification.link)
    return redirect('notifications')


@login_required
def mark_all_notifications_read_view(request):
    """
    Marca todas as notificações pendentes do usuário como lidas.
    """
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
        messages.success(request, "Todas as notificações foram marcadas como lidas.")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'unread_count': 0})

    return redirect('notifications')


@login_required
def notification_delete_view(request, notification_id):
    """
    Exclui uma notificação específica pertencente ao usuário logado.
    """
    if request.method != 'POST':
        return redirect('notifications')

    notif = get_object_or_404(Notification, id=notification_id, user=request.user)
    notif.delete()
    unread_count = request.user.notifications.filter(is_read=False).count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'status': 'success', 'notification_id': notification_id, 'unread_count': unread_count})

    messages.success(request, "Notificação excluída com sucesso.")
    return redirect('notifications')


@login_required
def notification_batch_action_view(request):
    """
    Ações em lote para notificações: excluir selecionadas, marcar selecionadas como lidas,
    excluir todas as lidas, ou excluir todas.
    """
    if request.method != 'POST':
        return redirect('notifications')

    action = request.POST.get('action')
    notification_ids = request.POST.getlist('notification_ids')

    if not notification_ids and request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            action = data.get('action', action)
            notification_ids = data.get('notification_ids', [])
        except Exception:
            pass

    if action == 'delete_all_read':
        deleted, _ = request.user.notifications.filter(is_read=True).delete()
        msg_feedback = f"{deleted} notificação(ões) lida(s) excluída(s) com sucesso."
    elif action == 'delete_all':
        deleted, _ = request.user.notifications.all().delete()
        msg_feedback = "Todas as notificações foram excluídas."
    elif action == 'mark_all_read':
        updated = request.user.notifications.filter(is_read=False).update(is_read=True)
        msg_feedback = "Todas as notificações foram marcadas como lidas."
    elif not notification_ids:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'status': 'error', 'message': 'Nenhuma notificação selecionada.'}, status=400)
        messages.warning(request, "Nenhuma notificação foi selecionada.")
        return redirect('notifications')
    elif action == 'delete':
        user_notifs = request.user.notifications.filter(id__in=notification_ids)
        count = user_notifs.count()
        user_notifs.delete()
        msg_feedback = f"{count} notificação(ões) excluída(s) com sucesso."
    elif action == 'mark_read':
        user_notifs = request.user.notifications.filter(id__in=notification_ids)
        count = user_notifs.update(is_read=True)
        msg_feedback = f"{count} notificação(ões) marcada(s) como lida(s)."
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            return JsonResponse({'status': 'error', 'message': 'Ação inválida.'}, status=400)
        messages.error(request, "Ação inválida.")
        return redirect('notifications')

    unread_count = request.user.notifications.filter(is_read=False).count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'status': 'success',
            'message': msg_feedback,
            'unread_count': unread_count,
            'action': action
        })

    messages.success(request, msg_feedback)
    return redirect('notifications')


def tam_evaluation_view(request):
    """
    Formulário empírico de Aceitação de Tecnologia (TAM - Davis, 1989)
    para validação da plataforma CodeView com avaliadores externos (PA2).
    """
    pu_questions = [
        ('pu1', 'PU1: Pílulas Curtas', 'O formato de pílulas curtas em vídeo (< 90 segundos) agiliza meu aprendizado e me ajuda a assimilar conceitos de programação mais rápido do que aulas longas.'),
        ('pu2', 'PU2: Desafios Instantâneos', 'Resolver desafios práticos instantâneos logo após assistir à pílula aumenta a fixação e o entendimento real do código.'),
        ('pu3', 'PU3: Portfólio Vivo', 'A proposta de "Portfólio Vivo" (onde a própria atuação prática e certificados substituem o currículo em anexo) demonstra com mais precisão a competência real de um dev.'),
        ('pu4', 'PU4: Cronograma e Certificado com QR', 'O cronograma de estudos sugerido e as certificações digitais com QR Code público agregam valor concreto à minha carreira e credibilidade técnica.'),
        ('pu5', 'PU5: Utilidade Geral', 'No geral, considero o CodeView uma plataforma útil e vantajosa para o ecossistema de aprendizado e contratação em tecnologia.'),
    ]

    peou_questions = [
        ('peou1', 'PEOU1: Navegação Intuitiva', 'A navegação geral entre as telas (Feed, Mini Cursos, Perfis, DMs e Notificações) é clara e intuitiva.'),
        ('peou2', 'PEOU2: Clareza Visual', 'A interface visual é agradável, com tipografia legível, contraste adequado em modo escuro e boa disposição dos elementos.'),
        ('peou3', 'PEOU3: Resolução de Desafios', 'Foi fácil e compreensível submeter as respostas dos desafios técnicos e entender o feedback imediato do sistema.'),
        ('peou4', 'PEOU4: Progresso e Certificação', 'A visualização do progresso do curso e as instruções para emitir/baixar o certificado são claras e sem burocracia.'),
        ('peou5', 'PEOU5: Independência de Treinamento', 'Consegui operar as principais funções do CodeView sem necessidade de treinamento ou manual de instruções.'),
    ]

    atu_questions = [
        ('atu1', 'ATU1: Experiência Agradável', 'A experiência de utilizar o CodeView foi agradável, engajadora e estimulante.'),
        ('atu2', 'ATU2: Formato Moderno', 'A dinâmica de micro-vídeos verticais de programação é uma ideia atraente que moderniza o ensino tradicional de software.'),
        ('atu3', 'ATU3: Percepção Positiva', 'Minha percepção global em relação ao propósito e à identidade do CodeView é bastante positiva.'),
    ]

    biu_questions = [
        ('biu1', 'BIU1: Uso Recorrente', 'Eu utilizaria o CodeView com frequência no meu dia a dia para aprender novas tecnologias ou revisar tópicos de programação.'),
        ('biu2', 'BIU2: Recomendação a Colegas', 'Eu indicaria o CodeView para colegas estudantes, desenvolvedores ou recrutadores de tecnologia.'),
        ('biu3', 'BIU3: Preferência Formativa', 'Ao buscar resolver uma dúvida ou praticar um conceito pontual de código, eu preferiria recorrer ao CodeView antes de buscar cursos extensos ou tutoriais prolixos.'),
    ]

    likert_scale = [
        (1, '1', 'Discordo Totalmente'),
        (2, '2', 'Discordo Parcialmente'),
        (3, '3', 'Neutro / Indiferente'),
        (4, '4', 'Concordo Parcialmente'),
        (5, '5', 'Concordo Totalmente'),
    ]

    if request.method == 'POST':
        try:
            evaluator_name = request.POST.get('evaluator_name', '').strip()
            evaluator_email = request.POST.get('evaluator_email', '').strip()
            role = request.POST.get('role', '').strip()
            experience = request.POST.get('experience', '').strip()
            device = request.POST.get('device', '').strip()

            if not role or not experience or not device:
                messages.error(request, "Por favor, preencha os dados do seu perfil de atuação e dispositivo.")
                raise ValueError("Campos demográficos incompletos.")

            likert_values = {}
            for q_name, _, _ in pu_questions + peou_questions + atu_questions + biu_questions:
                val = request.POST.get(q_name)
                if not val or not val.isdigit() or int(val) not in range(1, 6):
                    messages.error(request, f"Por favor, responda a afirmativa '{q_name.upper()}' na escala de 1 a 5.")
                    raise ValueError(f"Campo {q_name} ausente ou inválido.")
                likert_values[q_name] = int(val)

            evaluation = TAMEvaluation.objects.create(
                user=request.user if request.user.is_authenticated else None,
                evaluator_name=evaluator_name,
                evaluator_email=evaluator_email,
                role=role,
                experience=experience,
                device=device,
                highlights=request.POST.get('highlights', '').strip(),
                difficulties=request.POST.get('difficulties', '').strip(),
                suggestions=request.POST.get('suggestions', '').strip(),
                **likert_values
            )

            return render(request, 'accounts/tam_success.html', {
                'evaluation': evaluation,
            })
        except ValueError:
            pass

    return render(request, 'accounts/tam_evaluation.html', {
        'role_choices': TAMEvaluation.ROLE_CHOICES,
        'experience_choices': TAMEvaluation.EXPERIENCE_CHOICES,
        'device_choices': TAMEvaluation.DEVICE_CHOICES,
        'pu_questions': pu_questions,
        'peou_questions': peou_questions,
        'atu_questions': atu_questions,
        'biu_questions': biu_questions,
        'likert_scale': likert_scale,
    })


@login_required
def admin_dashboard_view(request):
    """
    Painel exclusivo do Super Administrador (Admin Dashboard).
    Permite organizar e cadastrar palavras-chaves (Tecnologias),
    visualizar KPIs da plataforma e analisar respostas do formulário TAM com gráficos interativos.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, "Acesso restrito ao Administrador do CodeView.")
        return redirect('feed')

    from videos.models import Technology, Video
    from courses.models import Course

    # Ações POST: Cadastrar, alternar e remover tecnologias / palavras-chaves
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_technology':
            name = request.POST.get('name', '').strip()
            icon_name = request.POST.get('icon_name', '').strip()
            is_active = request.POST.get('is_active') == 'on'

            if not name:
                messages.error(request, "O nome da palavra-chave / tecnologia é obrigatório.")
            elif Technology.objects.filter(name__iexact=name).exists():
                messages.error(request, f"A tecnologia '{name}' já está cadastrada.")
            else:
                tech = Technology.objects.create(
                    name=name,
                    icon_name=icon_name or '⚡',
                    is_active=is_active
                )
                messages.success(request, f"Palavra-chave / Tecnologia '{tech.name}' cadastrada com sucesso!")
            return redirect('admin_dashboard')

        elif action == 'toggle_technology':
            tech_id = request.POST.get('technology_id')
            tech = get_object_or_404(Technology, id=tech_id)
            tech.is_active = not tech.is_active
            tech.save()
            status_text = "ativada" if tech.is_active else "desativada"
            messages.success(request, f"Tecnologia '{tech.name}' {status_text} com sucesso!")
            return redirect('admin_dashboard')

        elif action == 'delete_technology':
            tech_id = request.POST.get('technology_id')
            tech = get_object_or_404(Technology, id=tech_id)
            if tech.videos.exists() or tech.courses.exists():
                tech.is_active = False
                tech.save()
                messages.warning(request, f"A tecnologia '{tech.name}' possui pílulas ou cursos vinculados. Ela foi desativada em vez de excluída para manter a integridade dos dados.")
            else:
                tech_name = tech.name
                tech.delete()
                messages.success(request, f"Tecnologia '{tech_name}' removida com sucesso!")
            return redirect('admin_dashboard')

    # Métricas Gerais
    total_users = User.objects.count()
    total_videos = Video.objects.count()
    total_courses = Course.objects.count()
    total_technologies = Technology.objects.count()

    technologies = Technology.objects.annotate(
        videos_count=Count('videos', distinct=True),
        courses_count=Count('courses', distinct=True)
    ).order_by('-is_active', 'name')

    tam_evaluations = TAMEvaluation.objects.select_related('user').order_by('-created_at')
    total_tam = tam_evaluations.count()

    # Opções e Nomes Amigáveis para Perfis Profissionais (TAM)
    ROLE_CHOICES_ORDER = [
        ('estudante', 'Estudante'),
        ('dev_junior', 'Dev Júnior'),
        ('dev_pleno_senior', 'Dev Pleno / Sênior'),
        ('recruiter', 'Recrutador / RH'),
        ('professor', 'Professor / Mentor'),
        ('outro', 'Outros'),
    ]

    roles_analytics = {}

    if total_tam > 0:
        avg_pu = round(sum(e.pu_score for e in tam_evaluations) / total_tam, 2)
        avg_peou = round(sum(e.peou_score for e in tam_evaluations) / total_tam, 2)
        avg_atu = round(sum(e.atu_score for e in tam_evaluations) / total_tam, 2)
        avg_biu = round(sum(e.biu_score for e in tam_evaluations) / total_tam, 2)
        avg_overall = round(sum(e.overall_score for e in tam_evaluations) / total_tam, 2)

        chart_tam_labels = ['PU (Utilidade)', 'PEOU (Facilidade)', 'ATU (Atitude)', 'BIU (Intenção)', 'Média Geral']
        chart_tam_data = [avg_pu, avg_peou, avg_atu, avg_biu, avg_overall]

        devices_map = {'desktop': 0, 'mobile': 0, 'tablet': 0}
        for e in tam_evaluations:
            devices_map[e.device] = devices_map.get(e.device, 0) + 1
        chart_devices_labels = ['Computador / Desktop', 'Smartphone / Celular', 'Tablet']
        chart_devices_data = [devices_map.get('desktop', 0), devices_map.get('mobile', 0), devices_map.get('tablet', 0)]

        # Estatísticas por perfil profissional
        roles_analytics['all'] = {
            'label': 'Todos os Perfis (Consolidado)',
            'short_label': 'Todos',
            'count': total_tam,
            'percentage': 100.0,
            'avg_pu': avg_pu,
            'avg_peou': avg_peou,
            'avg_atu': avg_atu,
            'avg_biu': avg_biu,
            'avg_overall': avg_overall,
        }

        chart_roles_labels = []
        chart_roles_counts = []
        chart_roles_scores = []

        for r_key, r_label in ROLE_CHOICES_ORDER:
            role_evals = [e for e in tam_evaluations if e.role == r_key]
            r_count = len(role_evals)
            if r_count > 0:
                r_avg_pu = round(sum(e.pu_score for e in role_evals) / r_count, 2)
                r_avg_peou = round(sum(e.peou_score for e in role_evals) / r_count, 2)
                r_avg_atu = round(sum(e.atu_score for e in role_evals) / r_count, 2)
                r_avg_biu = round(sum(e.biu_score for e in role_evals) / r_count, 2)
                r_avg_overall = round(sum(e.overall_score for e in role_evals) / r_count, 2)
                r_pct = round((r_count / total_tam) * 100, 1)
            else:
                r_avg_pu = r_avg_peou = r_avg_atu = r_avg_biu = r_avg_overall = 0.0
                r_pct = 0.0

            roles_analytics[r_key] = {
                'label': r_label,
                'short_label': r_label,
                'count': r_count,
                'percentage': r_pct,
                'avg_pu': r_avg_pu,
                'avg_peou': r_avg_peou,
                'avg_atu': r_avg_atu,
                'avg_biu': r_avg_biu,
                'avg_overall': r_avg_overall,
            }

            chart_roles_labels.append(r_label)
            chart_roles_counts.append(r_count)
            chart_roles_scores.append(r_avg_overall)

    else:
        avg_pu = avg_peou = avg_atu = avg_biu = avg_overall = 0.0
        chart_tam_labels = ['PU (Utilidade)', 'PEOU (Facilidade)', 'ATU (Atitude)', 'BIU (Intenção)', 'Média Geral']
        chart_tam_data = [0, 0, 0, 0, 0]
        chart_devices_labels = ['Computador / Desktop', 'Smartphone / Celular', 'Tablet']
        chart_devices_data = [0, 0, 0]
        chart_roles_labels = [r_label for _, r_label in ROLE_CHOICES_ORDER]
        chart_roles_counts = [0] * len(ROLE_CHOICES_ORDER)
        chart_roles_scores = [0.0] * len(ROLE_CHOICES_ORDER)

        roles_analytics['all'] = {
            'label': 'Todos os Perfis (Consolidado)',
            'short_label': 'Todos',
            'count': 0,
            'percentage': 0.0,
            'avg_pu': 0.0,
            'avg_peou': 0.0,
            'avg_atu': 0.0,
            'avg_biu': 0.0,
            'avg_overall': 0.0,
        }
        for r_key, r_label in ROLE_CHOICES_ORDER:
            roles_analytics[r_key] = {
                'label': r_label,
                'short_label': r_label,
                'count': 0,
                'percentage': 0.0,
                'avg_pu': 0.0,
                'avg_peou': 0.0,
                'avg_atu': 0.0,
                'avg_biu': 0.0,
                'avg_overall': 0.0,
            }

    context = {
        'total_users': total_users,
        'total_videos': total_videos,
        'total_courses': total_courses,
        'total_technologies': total_technologies,
        'technologies': technologies,
        'tam_evaluations': tam_evaluations,
        'total_tam': total_tam,
        'avg_pu': avg_pu,
        'avg_peou': avg_peou,
        'avg_atu': avg_atu,
        'avg_biu': avg_biu,
        'avg_overall': avg_overall,
        'roles_analytics': roles_analytics,
        'roles_analytics_json': json.dumps(roles_analytics),
        'chart_tam_labels_json': json.dumps(chart_tam_labels),
        'chart_tam_data_json': json.dumps(chart_tam_data),
        'chart_devices_labels_json': json.dumps(chart_devices_labels),
        'chart_devices_data_json': json.dumps(chart_devices_data),
        'chart_roles_labels_json': json.dumps(chart_roles_labels),
        'chart_roles_data_json': json.dumps(chart_roles_counts),
        'chart_roles_scores_data_json': json.dumps(chart_roles_scores),
    }

    return render(request, 'admin/custom_dashboard.html', context)

