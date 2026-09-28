from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from videos.models import Technology, Video
import os

User = get_user_model()


class Command(BaseCommand):
    help = "Popula o banco de dados com tecnologias e vídeos iniciais para teste da Onda 1."

    def handle(self, *args, **options):
        # 1. Obter ou criar autor padrão
        author = User.objects.filter(is_superuser=True).first()
        if not author:
            author = User.objects.create_superuser('admin@codeview.com', 'admin12345', first_name='Admin')

        # 2. Criar Tecnologias
        tech_data = [
            {'name': 'Python', 'slug': 'python', 'icon_name': '🐍'},
            {'name': 'JavaScript', 'slug': 'javascript', 'icon_name': '⚡'},
            {'name': 'Django', 'slug': 'django', 'icon_name': '🎯'},
            {'name': 'SQL & Banco de Dados', 'slug': 'sql', 'icon_name': '🗄️'},
        ]

        technologies = {}
        for t in tech_data:
            tech, created = Technology.objects.get_or_create(
                slug=t['slug'],
                defaults={'name': t['name'], 'icon_name': t['icon_name'], 'is_active': True}
            )
            technologies[t['slug']] = tech
            self.stdout.write(self.style.SUCCESS(f"Tecnologia pronta: {tech.name}"))

        # 3. Criar Vídeos
        sample_videos = [
            {
                'title': 'List Comprehensions em 45 segundos',
                'description': 'Aprenda a transformar loops for tradicionais em expressões de uma linha limpas e idiomáticas em Python.',
                'tech': technologies['python'],
                'file': 'videos/sample_python.mp4',
                'duration': 45,
            },
            {
                'title': 'Async / Await no JavaScript Descomplicado',
                'description': 'Como lidar com promessas e operações assíncronas de forma legível sem cair no callback hell.',
                'tech': technologies['javascript'],
                'file': 'videos/sample_js.mp4',
                'duration': 50,
            },
            {
                'title': 'Custom User Model no Django sem dor',
                'description': 'Por que você deve sempre herdar de AbstractUser e usar o e-mail como chave antes da primeira migração.',
                'tech': technologies['django'],
                'file': 'videos/sample_django.mp4',
                'duration': 60,
            },
            {
                'title': 'Macetes de Dicionários e Métodos .get()',
                'description': 'Evite KeyError no Python e forneça valores default seguros com este truque prático de dicionários.',
                'tech': technologies['python'],
                'file': 'videos/sample_python.mp4',
                'duration': 35,
            },
        ]

        for v in sample_videos:
            video, created = Video.objects.get_or_create(
                title=v['title'],
                defaults={
                    'description': v['description'],
                    'technology': v['tech'],
                    'author': author,
                    'video_file': v['file'],
                    'duration_seconds': v['duration'],
                    'is_published': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Vídeo cadastrado: {video.title}"))

        self.stdout.write(self.style.SUCCESS("Catálogo da Onda 1 semeado com sucesso!"))
