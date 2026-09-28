from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Technology, Video

User = get_user_model()


class TechnologyModelTest(TestCase):
    """
    Testes de unidade para o modelo Technology.
    """
    def test_create_technology_and_auto_slug(self):
        tech = Technology.objects.create(name="Django Framework", icon_name="🎯")
        self.assertEqual(tech.name, "Django Framework")
        self.assertEqual(tech.slug, "django-framework")
        self.assertEqual(str(tech), "Django Framework")
        self.assertTrue(tech.is_active)

    def test_custom_slug_preserved(self):
        tech = Technology.objects.create(name="PostgreSQL", slug="postgres", icon_name="🐘")
        self.assertEqual(tech.slug, "postgres")


class VideoModelTest(TestCase):
    """
    Testes de unidade para o modelo Video (Pílulas de Micro-Vídeo 9:16).
    """
    def setUp(self):
        self.user = User.objects.create_user(
            email="creator@codeview.com",
            password="Password123!",
            first_name="Criador"
        )
        self.tech = Technology.objects.create(name="Python", slug="python", icon_name="🐍")
        self.dummy_video = SimpleUploadedFile(
            "test_video.mp4",
            b"fake mp4 video content",
            content_type="video/mp4"
        )

    def test_create_video(self):
        video = Video.objects.create(
            title="Dicas de List Comprehension",
            description="Aprenda em 45 segundos sintaxe limpa.",
            technology=self.tech,
            author=self.user,
            video_file=self.dummy_video,
            duration_seconds=45,
            is_published=True
        )
        self.assertEqual(str(video), "Dicas de List Comprehension (Python)")
        self.assertEqual(video.views_count, 0)
        self.assertEqual(video.duration_seconds, 45)
        self.assertTrue(video.is_published)


class FeedViewIntegrationTest(TestCase):
    """
    Testes de integração para a view do Feed vertical e filtros por tecnologia.
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="student@codeview.com",
            password="Password123!",
            first_name="Aluno"
        )
        self.tech_python = Technology.objects.create(name="Python", slug="python", icon_name="🐍")
        self.tech_js = Technology.objects.create(name="JavaScript", slug="javascript", icon_name="⚡")
        self.tech_empty = Technology.objects.create(name="Rust", slug="rust", icon_name="🦀")

        dummy_file = SimpleUploadedFile("dummy.mp4", b"data", content_type="video/mp4")

        # Vídeo 1: Python (Publicado)
        self.video_python = Video.objects.create(
            title="Python Loops",
            description="Loops em Python",
            technology=self.tech_python,
            author=self.user,
            video_file=dummy_file,
            is_published=True
        )

        # Vídeo 2: JavaScript (Publicado)
        self.video_js = Video.objects.create(
            title="JS Promises",
            description="Promises no JS",
            technology=self.tech_js,
            author=self.user,
            video_file=dummy_file,
            is_published=True
        )

        # Vídeo 3: Python (Não Publicado / Rascunho)
        self.video_draft = Video.objects.create(
            title="Python Rascunho",
            description="Não publicado",
            technology=self.tech_python,
            author=self.user,
            video_file=dummy_file,
            is_published=False
        )

    def test_feed_requires_login(self):
        """Acesso anônimo deve redirecionar para a tela de login com ?next=/feed/"""
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_feed_view_authenticated_shows_all_published_videos(self):
        """Usuário autenticado deve visualizar todos os vídeos publicados no feed padrão."""
        self.client.login(email="student@codeview.com", password="Password123!")
        response = self.client.get(reverse('feed'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'videos/feed.html')

        videos_in_context = list(response.context['videos'])
        self.assertIn(self.video_python, videos_in_context)
        self.assertIn(self.video_js, videos_in_context)
        self.assertNotIn(self.video_draft, videos_in_context)
        self.assertEqual(len(videos_in_context), 2)

    def test_feed_filter_by_technology(self):
        """Filtro ?tech=python deve retornar apenas vídeos da tecnologia solicitada."""
        self.client.login(email="student@codeview.com", password="Password123!")
        response = self.client.get(reverse('feed'), {'tech': 'python'})
        self.assertEqual(response.status_code, 200)

        videos_in_context = list(response.context['videos'])
        self.assertIn(self.video_python, videos_in_context)
        self.assertNotIn(self.video_js, videos_in_context)
        self.assertEqual(len(videos_in_context), 1)
        self.assertEqual(response.context['current_tech'], 'python')
        self.assertEqual(response.context['current_technology'], self.tech_python)

    def test_feed_empty_state_for_technology_without_videos(self):
        """Filtro para tecnologia sem vídeos deve renderizar o empty state."""
        self.client.login(email="student@codeview.com", password="Password123!")
        response = self.client.get(reverse('feed'), {'tech': 'rust'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['videos']), 0)
        self.assertContains(response, "Nenhum vídeo encontrado")
        self.assertContains(response, "Rust")

    def test_home_url_renders_feed(self):
        """A URL raiz '/' aponta para o feed_view e requer autenticação."""
        self.client.login(email="student@codeview.com", password="Password123!")
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'videos/feed.html')


class SeedCommandTest(TestCase):
    """
    Testes para o comando seed_codeview.
    """
    def test_seed_command_execution(self):
        call_command('seed_codeview')
        # Verifica se as 4 tecnologias foram criadas
        self.assertTrue(Technology.objects.filter(slug='python').exists())
        self.assertTrue(Technology.objects.filter(slug='javascript').exists())
        self.assertTrue(Technology.objects.filter(slug='django').exists())
        self.assertTrue(Technology.objects.filter(slug='sql').exists())
        # Verifica se os vídeos de exemplo foram criados
        self.assertGreaterEqual(Video.objects.filter(is_published=True).count(), 4)
