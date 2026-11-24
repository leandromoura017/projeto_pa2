import json
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


class VideoPublishAndLikeTests(TestCase):
    """
    Testes da Onda 3: Publicar vídeo (upload) e Curtir vídeos no feed.
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="creator_onda3@codeview.com",
            password="Password123!",
            first_name="Criador"
        )
        self.tech = Technology.objects.create(name="Python", slug="python", icon_name="🐍")

    def test_publish_video_view_creates_video(self):
        self.client.force_login(self.user)
        get_res = self.client.get(reverse('video_publish'))
        self.assertEqual(get_res.status_code, 200)
        self.assertTemplateUsed(get_res, 'videos/publish.html')

        video_file = SimpleUploadedFile("novo_video.mp4", b"fake-mp4-bytes", content_type="video/mp4")
        post_res = self.client.post(reverse('video_publish'), {
            'title': 'Dica Rápida de Decorators',
            'technology': self.tech.id,
            'description': 'Como usar @property em Python.',
            'duration_seconds': 40,
            'video_file': video_file,
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertTrue(Video.objects.filter(title='Dica Rápida de Decorators', author=self.user).exists())

    def test_toggle_video_like_ajax(self):
        from .models import VideoLike
        self.client.force_login(self.user)
        video = Video.objects.create(
            title="Vídeo para Curtir",
            technology=self.tech,
            author=self.user,
            video_file=SimpleUploadedFile("like.mp4", b"bytes", content_type="video/mp4"),
            is_published=True
        )
        url = reverse('video_like', kwargs={'video_id': video.id})

        # 1ª chamada: curte
        res1 = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        self.assertTrue(data1['liked'])
        self.assertEqual(data1['likes_count'], 1)
        self.assertTrue(VideoLike.objects.filter(user=self.user, video=video).exists())

        # 2ª chamada: descurte
        res2 = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertFalse(data2['liked'])
        self.assertEqual(data2['likes_count'], 0)
        self.assertFalse(VideoLike.objects.filter(user=self.user, video=video).exists())


class VideoShareAndNotificationTests(TestCase):
    """
    Testes da Onda 5:
    Item #22: Compartilhar vídeo (página pública com player 9:16 e links sociais).
    Item #23: Notificação automática ao publicar novo vídeo.
    """
    def setUp(self):
        self.client = Client()
        self.creator = User.objects.create_user(
            email='creator5@codeview.com',
            password='Password123!',
            first_name='Criador 5'
        )
        self.subscriber = User.objects.create_user(
            email='subscriber5@codeview.com',
            password='Password123!',
            first_name='Aluno Inscrito'
        )
        self.tech = Technology.objects.create(name='TypeScript', slug='typescript', icon_name='🔷')
        self.dummy_file = SimpleUploadedFile("ts_tip.mp4", b"ts content", content_type="video/mp4")
        self.video = Video.objects.create(
            title='Generics em TypeScript no Dia a Dia',
            description='Domine tipos flexíveis e reutilizáveis em 50 segundos.',
            technology=self.tech,
            author=self.creator,
            video_file=self.dummy_file,
            duration_seconds=50,
            is_published=True
        )

    def test_video_detail_view_increments_views_and_renders_share_page(self):
        url = reverse('video_detail', kwargs={'video_id': self.video.id})
        initial_views = self.video.views_count

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'videos/video_detail.html')
        self.assertContains(response, 'Generics em TypeScript no Dia a Dia')
        self.assertContains(response, 'Compartilhar Pílula de Código')

        self.video.refresh_from_db()
        self.assertEqual(self.video.views_count, initial_views + 1)

    def test_publishing_video_creates_notifications_for_other_users(self):
        from accounts.models import Notification
        from courses.models import Course, Enrollment

        # Inscreve self.subscriber em um curso da mesma tecnologia para qualificar a notificação
        course = Course.objects.create(
            title='TypeScript Essencial',
            technology=self.tech,
            instructor=self.creator,
            estimated_minutes=60
        )
        Enrollment.objects.create(user=self.subscriber, course=course, is_active=True)

        # Cria usuário sem qualquer relação com a tecnologia
        unrelated_user = User.objects.create_user(
            email='unrelated5@codeview.com',
            password='Password123!',
            first_name='Sem Interesse'
        )

        self.client.force_login(self.creator)

        new_video_file = SimpleUploadedFile("clean_code.mp4", b"clean code bytes", content_type="video/mp4")
        res = self.client.post(reverse('video_publish'), {
            'title': '3 Regras de Clean Code',
            'technology': self.tech.id,
            'description': 'Código legível e fácil de manter.',
            'duration_seconds': 45,
            'video_file': new_video_file,
        })
        self.assertEqual(res.status_code, 302)

        # O aluno matriculado na tecnologia deve ter recebido a notificação
        notif = Notification.objects.filter(
            user=self.subscriber,
            title__icontains='Nova pílula'
        ).first()
        self.assertIsNotNone(notif)
        self.assertIn('3 Regras de Clean Code', notif.message)
        self.assertEqual(notif.icon, '🎬')

        # O usuário não matriculado e sem a tecnologia no perfil NÃO deve receber
        unrelated_notif = Notification.objects.filter(user=unrelated_user).first()
        self.assertIsNone(unrelated_notif)



class VideoCommentTests(TestCase):
    """
    Testes da Onda 6:
    Item #24: Aba / Seção de comentários em vídeos.
    """
    def setUp(self):
        self.client = Client()
        self.creator = User.objects.create_user(
            email='creator_comment@codeview.com',
            password='Password123!',
            first_name='Criador Coment'
        )
        self.commenter = User.objects.create_user(
            email='student_comment@codeview.com',
            password='Password123!',
            first_name='Estudante Coment'
        )
        self.tech = Technology.objects.create(name='Python', slug='python', icon_name='🐍')
        self.dummy_file = SimpleUploadedFile("com_video.mp4", b"bytes", content_type="video/mp4")
        self.video = Video.objects.create(
            title='Como funciona o GIL em Python',
            description='Explicação rápida do Global Interpreter Lock.',
            technology=self.tech,
            author=self.creator,
            video_file=self.dummy_file,
            duration_seconds=45,
            is_published=True
        )

    def test_add_video_comment_authenticated(self):
        self.client.force_login(self.commenter)
        url = reverse('video_comment', kwargs={'video_id': self.video.id})

        response = self.client.post(url, {'content': 'Excelente explicação! Me ajudou muito.'})
        self.assertEqual(response.status_code, 302)

        from .models import VideoComment
        comment = VideoComment.objects.filter(video=self.video, user=self.commenter).first()
        self.assertIsNotNone(comment)
        self.assertEqual(comment.content, 'Excelente explicação! Me ajudou muito.')
        self.assertEqual(self.video.comments_count, 1)

    def test_commenting_by_other_user_notifies_video_author(self):
        from accounts.models import Notification
        self.client.force_login(self.commenter)
        url = reverse('video_comment', kwargs={'video_id': self.video.id})

        self.client.post(url, {'content': 'Dúvida: isso afeta multiprocessing?'})

        notif = Notification.objects.filter(user=self.creator, title__icontains='Novo comentário').first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.icon, '💬')
        self.assertIn('multiprocessing', notif.message)

    def test_empty_comment_rejected(self):
        self.client.force_login(self.commenter)
        url = reverse('video_comment', kwargs={'video_id': self.video.id})

        res = self.client.post(url, {'content': '   '})
        self.assertEqual(res.status_code, 302)

        from .models import VideoComment
        self.assertFalse(VideoComment.objects.filter(video=self.video).exists())


class Onda7VideoTests(TestCase):
    """
    Testes da Onda 7:
    Item #28: Anotações privadas nos vídeos.
    Item #29: Selo/votação 'Conteúdo Confiável'.
    """
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(
            email='author7@codeview.com',
            password='Password123!',
            first_name='Autor Onda 7'
        )
        self.student = User.objects.create_user(
            email='student7@codeview.com',
            password='Password123!',
            first_name='Aluno Onda 7'
        )
        self.mentor = User.objects.create_user(
            email='mentor7@codeview.com',
            password='Password123!',
            first_name='Mentor Onda 7'
        )
        p = self.mentor.profile
        p.is_mentor = True
        p.save()
        self.mentor.refresh_from_db()

        self.tech = Technology.objects.create(name='Go', slug='go', icon_name='🐹')
        self.dummy_file = SimpleUploadedFile("go.mp4", b"go bytes", content_type="video/mp4")
        self.video = Video.objects.create(
            title='Goroutines e Channels em 60s',
            description='Concorrência simplificada.',
            technology=self.tech,
            author=self.author,
            video_file=self.dummy_file,
            duration_seconds=60,
            is_published=True
        )

    def test_save_private_note(self):
        from .models import VideoNote
        self.client.force_login(self.student)
        url = reverse('video_note', kwargs={'video_id': self.video.id})

        response = self.client.post(url, {'content': 'go func() dispara goroutine leve.'})
        self.assertEqual(response.status_code, 302)

        note = VideoNote.objects.filter(user=self.student, video=self.video).first()
        self.assertIsNotNone(note)
        self.assertEqual(note.content, 'go func() dispara goroutine leve.')

        # Verificar se a anotação é renderizada na página de detalhes
        detail_res = self.client.get(reverse('video_detail', kwargs={'video_id': self.video.id}))
        self.assertContains(detail_res, 'go func() dispara goroutine leve.')

    def test_save_private_note_ajax(self):
        from .models import VideoNote
        self.client.force_login(self.student)
        url = reverse('video_note', kwargs={'video_id': self.video.id})

        res = self.client.post(
            url,
            data=json.dumps({'content': 'Nota via AJAX'}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['content'], 'Nota via AJAX')
        self.assertTrue(VideoNote.objects.filter(user=self.student, video=self.video, content='Nota via AJAX').exists())

    def test_trust_vote_toggle_and_mentor_verified_seal(self):
        from .models import VideoTrustVote
        from accounts.models import Notification

        self.client.force_login(self.mentor)
        url = reverse('video_trust_vote', kwargs={'video_id': self.video.id})

        # 1. Mentor vota confiável
        res = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['is_trusted'])
        self.assertEqual(data['trust_count'], 1)
        self.assertTrue(data['is_verified_content'])

        # Notificação disparada para o autor
        notif = Notification.objects.filter(user=self.author, title__icontains='Selo de Confiança').first()
        self.assertIsNotNone(notif)
        self.assertIn('Goroutines e Channels', notif.message)
        self.assertEqual(notif.icon, '🛡️')

        # 2. Mentor retira o voto
        res2 = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data2 = res2.json()
        self.assertFalse(data2['is_trusted'])
        self.assertEqual(data2['trust_count'], 0)


class Onda8CameraRecordingTests(TestCase):
    """
    Testes para a Aba de Câmera (Gravação Direta no Navegador - Onda 8 - #34).
    """
    def setUp(self):
        self.client = Client()
        self.creator = User.objects.create_user(
            email='camera.creator@codeview.com',
            password='Password123!',
            first_name='CamCreator'
        )
        self.tech = Technology.objects.create(name='TypeScript', slug='typescript', icon_name='🔷')

    def test_publish_page_renders_camera_tab_and_webrtc_elements(self):
        self.client.force_login(self.creator)
        url = reverse('video_publish')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Gravar da Câmera (9:16)')
        self.assertContains(res, 'panel-camera')
        self.assertContains(res, 'camera-stream')
        self.assertContains(res, 'recorded-preview')
        self.assertContains(res, 'btn-record')
        self.assertContains(res, 'btn-stop')
        self.assertContains(res, '9:16 vertical')

    def test_publish_video_from_camera_webm_blob_upload(self):
        self.client.force_login(self.creator)
        url = reverse('video_publish')
        camera_webm_file = SimpleUploadedFile(
            'gravacao_pilula_12345.webm',
            b'RIFF....WEBM....fake-vertical-webm-data',
            content_type='video/webm'
        )

        payload = {
            'title': 'TypeScript Generics em 40 segundos',
            'technology': self.tech.id,
            'description': 'Exemplo prático de generic constraints gravado direto da câmera.',
            'video_file': camera_webm_file,
            'duration_seconds': 40
        }

        res = self.client.post(url, data=payload)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('feed'))

        video = Video.objects.filter(title='TypeScript Generics em 40 segundos').first()
        self.assertIsNotNone(video)
        self.assertEqual(video.author, self.creator)
        self.assertEqual(video.technology, self.tech)
        self.assertEqual(video.duration_seconds, 40)
        self.assertTrue(video.video_file.name.endswith('.webm'))


class VideoValidationAndAdaptivePlayerTests(TestCase):
    """
    Testes para validação estrita de vídeos (bloqueio de imagens)
    e dinâmica adaptativa proporcional do player com Tela Cheia (estilo TikTok).
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='tester_tiktok@codeview.com',
            password='Password123!',
            first_name='Tester'
        )
        self.tech = Technology.objects.create(name='Python', slug='python', icon_name='🐍')
        self.client.force_login(self.user)

    def test_upload_image_fails_form_validation(self):
        """Envio de imagem PNG deve ser rejeitado pelo formulário de publicação."""
        fake_png = SimpleUploadedFile(
            'screenshot.png',
            b'\x89PNG\r\n\x1a\nfake-image-bytes',
            content_type='image/png'
        )
        payload = {
            'title': 'Tentativa de Upload de Imagem',
            'technology': self.tech.id,
            'description': 'Não deve ser aceito',
            'duration_seconds': 30,
            'video_file': fake_png
        }
        res = self.client.post(reverse('video_publish'), data=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn('video_file', res.context['form'].errors)
        error_msg = res.context['form'].errors['video_file'][0]
        self.assertIn('imagem', error_msg.lower())
        self.assertFalse(Video.objects.filter(title='Tentativa de Upload de Imagem').exists())

    def test_upload_jpeg_fails_form_validation(self):
        """Envio de imagem JPEG deve ser rejeitado pelo formulário de publicação."""
        fake_jpg = SimpleUploadedFile(
            'foto.jpeg',
            b'\xff\xd8\xfffake-jpeg-bytes',
            content_type='image/jpeg'
        )
        payload = {
            'title': 'Tentativa com JPEG',
            'technology': self.tech.id,
            'description': 'Não deve ser aceito',
            'duration_seconds': 30,
            'video_file': fake_jpg
        }
        res = self.client.post(reverse('video_publish'), data=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn('video_file', res.context['form'].errors)
        self.assertFalse(Video.objects.filter(title='Tentativa com JPEG').exists())

    def test_validate_video_file_direct(self):
        """Função validate_video_file deve lançar ValidationError para imagens."""
        from django.core.exceptions import ValidationError
        from .models import validate_video_file

        fake_png = SimpleUploadedFile('teste.png', b'data', content_type='image/png')
        with self.assertRaises(ValidationError):
            validate_video_file(fake_png)

        fake_webp = SimpleUploadedFile('teste.webp', b'data', content_type='image/webp')
        with self.assertRaises(ValidationError):
            validate_video_file(fake_webp)

        valid_mp4 = SimpleUploadedFile('video.mp4', b'data', content_type='video/mp4')
        # Não deve lançar exceção
        validate_video_file(valid_mp4)

    def test_feed_renders_fullscreen_button_and_contain_class(self):
        """O Feed deve renderizar o botão Tela Cheia e a classe adaptativa object-contain."""
        valid_video = SimpleUploadedFile('reel.mp4', b'data', content_type='video/mp4')
        video = Video.objects.create(
            title='Vídeo Horizontal de Teste',
            technology=self.tech,
            author=self.user,
            video_file=valid_video,
            is_published=True
        )
        res = self.client.get(reverse('feed'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'object-contain')
        self.assertContains(res, 'btn-fullscreen')
        self.assertContains(res, 'Tela Cheia')

    def test_video_detail_renders_fullscreen_button_and_contain_class(self):
        """A página de detalhes do vídeo deve renderizar o botão Tela Cheia e a classe object-contain."""
        valid_video = SimpleUploadedFile('reel_detail.mp4', b'data', content_type='video/mp4')
        video = Video.objects.create(
            title='Vídeo Detalhe Adaptativo',
            technology=self.tech,
            author=self.user,
            video_file=valid_video,
            is_published=True
        )
        res = self.client.get(reverse('video_detail', kwargs={'video_id': video.id}))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'object-contain')
        self.assertContains(res, 'btn-detail-fullscreen')
        self.assertContains(res, 'Tela Cheia')


