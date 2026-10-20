from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse
from .models import Technology, Video, VideoLike
from .forms import VideoPublishForm


@login_required
def feed_view(request):
    """
    Feed principal de micro-vídeos verticais (formato TikTok 9:16)
    com suporte a filtragem dinâmica por tecnologia, busca textual e curtidas.
    """
    tech_slug = request.GET.get('tech', '').strip()
    query = request.GET.get('q', '').strip()
    
    technologies = Technology.objects.filter(is_active=True).order_by('name')
    videos = Video.objects.filter(is_published=True).select_related('technology', 'author').prefetch_related('likes', 'lessons')

    current_technology = None
    if tech_slug:
        videos = videos.filter(technology__slug=tech_slug)
        current_technology = technologies.filter(slug=tech_slug).first()

    if query:
        videos = videos.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(technology__name__icontains=query)
        )

    liked_video_ids = set(
        VideoLike.objects.filter(user=request.user).values_list('video_id', flat=True)
    )

    return render(request, 'videos/feed.html', {
        'videos': videos,
        'technologies': technologies,
        'current_tech': tech_slug,
        'current_technology': current_technology,
        'query': query,
        'liked_video_ids': liked_video_ids,
    })


@login_required
def publish_video_view(request):
    """
    Tela e processamento de publicação (upload) de novo micro-vídeo no feed (Onda 3)
    com disparo automático de alerta/notificação para outros membros (Onda 5 - #23).
    """
    if request.method == 'POST':
        form = VideoPublishForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.author = request.user
            video.is_published = True
            video.save()

            # Disparo de Notificações / Alerta no Sininho (Onda 5 - #23)
            from accounts.models import User, Notification
            other_users = User.objects.filter(is_active=True).exclude(id=request.user.id)
            author_name = request.user.first_name or request.user.username
            video_share_url = reverse('video_detail', kwargs={'video_id': video.id})
            
            notifications = [
                Notification(
                    user=u,
                    title=f"Nova pílula de {video.technology.name}!",
                    message=f"{author_name} publicou '{video.title}'. Assista agora!",
                    link=video_share_url,
                    icon='🎬'
                )
                for u in other_users
            ]
            if notifications:
                Notification.objects.bulk_create(notifications)

            messages.success(request, f"Vídeo '{video.title}' publicado com sucesso no Feed!")
            return redirect('feed')
    else:
        form = VideoPublishForm()

    return render(request, 'videos/publish.html', {
        'form': form,
    })


@login_required
def toggle_video_like_view(request, video_id):
    """
    Alterna curtida (like/unlike) do usuário autenticado em um vídeo do feed (Onda 3).
    Suporta resposta JSON para atualização instantânea sem recarregar a página.
    """
    if request.method != 'POST':
        return redirect('feed')

    video = get_object_or_404(Video, id=video_id, is_published=True)
    like_obj, created = VideoLike.objects.get_or_create(user=request.user, video=video)

    if not created:
        like_obj.delete()
        liked = False
    else:
        liked = True

    likes_count = video.likes.count()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'status': 'success',
            'liked': liked,
            'likes_count': likes_count,
            'video_id': video.id,
        })

    return redirect('feed')


def video_detail_view(request, video_id):
    """
    Página individual de compartilhamento de vídeo público (Onda 5 - #22).
    Acessível via link direto compartilhado por redes sociais, WhatsApp ou no feed.
    """
    video = get_object_or_404(
        Video.objects.select_related('technology', 'author').prefetch_related('likes', 'lessons'),
        id=video_id,
        is_published=True
    )
    
    # Incrementa contador de visualizações
    Video.objects.filter(id=video.id).update(views_count=video.views_count + 1)
    video.views_count += 1

    is_liked = False
    if request.user.is_authenticated:
        is_liked = VideoLike.objects.filter(user=request.user, video=video).exists()

    absolute_url = request.build_absolute_uri()

    return render(request, 'videos/video_detail.html', {
        'video': video,
        'is_liked': is_liked,
        'absolute_url': absolute_url,
    })
