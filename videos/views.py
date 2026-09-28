from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Technology, Video


@login_required
def feed_view(request):
    """
    Feed principal de micro-vídeos verticais (formato TikTok 9:16)
    com suporte a filtragem dinâmica por tecnologia.
    """
    tech_slug = request.GET.get('tech', '').strip()
    
    technologies = Technology.objects.filter(is_active=True).order_by('name')
    videos = Video.objects.filter(is_published=True).select_related('technology', 'author')

    current_technology = None
    if tech_slug:
        videos = videos.filter(technology__slug=tech_slug)
        current_technology = technologies.filter(slug=tech_slug).first()

    return render(request, 'videos/feed.html', {
        'videos': videos,
        'technologies': technologies,
        'current_tech': tech_slug,
        'current_technology': current_technology,
    })
