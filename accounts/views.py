from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import JsonResponse
from .forms import SignUpForm, LoginForm, ProfileEditForm
from .models import User, Profile, DirectMessage, Notification


def _build_portfolio_context(target_user):
    """
    Constrói os indicadores e registros verificáveis do Portfólio Vivo de um usuário.
    """
    from courses.models import Enrollment, ChallengeAttempt, Certificate, LessonProgress

    profile, _ = Profile.objects.get_or_create(user=target_user)
    solved_attempts = ChallengeAttempt.objects.filter(
        user=target_user,
        is_correct=True
    ).select_related('challenge', 'challenge__lesson', 'challenge__lesson__course').order_by('-attempted_at')

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
    context = _build_portfolio_context(request.user)
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
    context = _build_portfolio_context(target_user)
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
