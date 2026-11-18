from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Profile, UserConsent

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        user = User.objects.create_user(
            email='carlinhos@example.com',
            password='TestPassword123!',
            first_name='Carlinhos'
        )
        self.assertEqual(user.email, 'carlinhos@example.com')
        self.assertEqual(user.first_name, 'Carlinhos')
        self.assertTrue(user.check_password('TestPassword123!'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='TestPassword123!')

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email='admin@codeview.com',
            password='AdminPassword123!',
            first_name='Admin'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_profile_auto_created_via_signal(self):
        user = User.objects.create_user(
            email='dev@example.com',
            password='Password123!'
        )
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.user, user)


class SignUpAndLGPDTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')

    def test_signup_page_loads_successfully(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')
        self.assertContains(response, 'LGPD')

    def test_signup_fails_without_lgpd_consent(self):
        response = self.client.post(self.signup_url, {
            'first_name': 'Carlos Aluno',
            'email': 'carlos@example.com',
            'password': 'SenhaSegura123!',
            'password_confirm': 'SenhaSegura123!',
            # lgpd_consent omisso
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='carlos@example.com').exists())
        self.assertFormError(response.context['form'], 'lgpd_consent', 'Você precisa concordar com os Termos de Privacidade para continuar.')

    def test_signup_successful_with_lgpd_consent(self):
        response = self.client.post(self.signup_url, {
            'first_name': 'Carlos Aluno',
            'email': 'carlos@example.com',
            'password': 'SenhaSegura123!',
            'password_confirm': 'SenhaSegura123!',
            'lgpd_consent': 'on'
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.filter(email='carlos@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'Carlos Aluno')
        consent = UserConsent.objects.filter(user=user).first()
        self.assertIsNotNone(consent)
        self.assertEqual(consent.terms_version, 'v1.0-2026')

    def test_signup_fails_with_duplicate_email(self):
        User.objects.create_user(email='duplicado@example.com', password='Password123!')
        response = self.client.post(self.signup_url, {
            'first_name': 'Outro Dev',
            'email': 'duplicado@example.com',
            'password': 'NovaSenhaSegura123!',
            'password_confirm': 'NovaSenhaSegura123!',
            'lgpd_consent': 'on'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'Este e-mail já está em uso.')

    def test_signup_fails_with_mismatched_passwords(self):
        response = self.client.post(self.signup_url, {
            'first_name': 'Dev Mismatch',
            'email': 'mismatch@example.com',
            'password': 'SenhaUm12345!',
            'password_confirm': 'OutraSenhaDiferente123!',
            'lgpd_consent': 'on'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'password_confirm', 'As senhas não coincidem.')


class AuthenticationViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='aluno@codeview.com',
            password='MinhaSenha123!',
            first_name='Aluno'
        )

    def test_login_successful_with_email(self):
        response = self.client.post(reverse('login'), {
            'email': 'aluno@codeview.com',
            'password': 'MinhaSenha123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_fails_with_wrong_password(self):
        response = self.client.post(reverse('login'), {
            'email': 'aluno@codeview.com',
            'password': 'SenhaErrada123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertContains(response, 'E-mail ou senha inválidos.')

    def test_logout_clears_session(self):
        self.client.login(username='aluno@codeview.com', password='MinhaSenha123!')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)


class LegalPagesTests(TestCase):
    def test_terms_page_loads(self):
        response = self.client.get(reverse('terms'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Termos de Uso')

    def test_privacy_page_loads(self):
        response = self.client.get(reverse('privacy'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'LGPD')


class ProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='carlinhos.dev@codeview.com',
            password='Password123!',
            first_name='Carlinhos',
            last_name='Dev'
        )

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_profile_view_loads_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertContains(response, 'Carlinhos Dev')
        self.assertContains(response, 'Portfólio Vivo')
        # Verifica regra de negócio anti-CV: nenhum campo de upload de currículo
        self.assertNotContains(response, 'name="curriculo"')
        self.assertNotContains(response, 'name="resume"')
        self.assertNotContains(response, 'name="cv"')

    def test_profile_edit_form_updates_profile(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('profile_edit'), {
            'first_name': 'Carlos',
            'last_name': 'Sabino',
            'bio': 'Desenvolvedor Python focado em backend e automações.',
            'github_url': 'https://github.com/carlinhos',
            'linkedin_url': 'https://linkedin.com/in/carlinhos',
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Carlos')
        self.assertEqual(self.user.last_name, 'Sabino')
        self.assertEqual(self.user.profile.bio, 'Desenvolvedor Python focado em backend e automações.')
        self.assertEqual(self.user.profile.github_url, 'https://github.com/carlinhos')

    def test_profile_avatar_upload_success(self):
        self.client.force_login(self.user)
        img_io = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='cyan')
        image.save(img_io, format='JPEG')
        img_file = SimpleUploadedFile("avatar.jpg", img_io.getvalue(), content_type="image/jpeg")

        response = self.client.post(reverse('profile_edit'), {
            'first_name': 'Carlos',
            'last_name': 'Dev',
            'bio': 'Bio com foto',
            'avatar': img_file,
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(bool(self.user.profile.avatar))
        self.assertIn('avatars/', self.user.profile.avatar.name)


class ProfileSearchAndDirectMessageTests(TestCase):
    """
    Testes da Onda 4: Busca de perfis (#16) e Aba de DMs para conversas com mentores (#19).
    Testes da Onda 6: Notificação automática ao receber mensagem (#26).
    """
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            email='aluno.dm@codeview.com',
            password='Password123!',
            first_name='Carlinhos',
            last_name='Sabino'
        )
        self.mentor = User.objects.create_user(
            email='mentora.dm@codeview.com',
            password='Password123!',
            first_name='Ana',
            last_name='Mentora'
        )
        self.mentor.profile.is_mentor = True
        self.mentor.profile.specialties = 'Python, Django & Arquitetura'
        self.mentor.profile.save()

    def test_profile_search_and_mentor_filter(self):
        self.client.force_login(self.student)
        res_all = self.client.get(reverse('profile_search'))
        self.assertEqual(res_all.status_code, 200)
        self.assertContains(res_all, 'Ana Mentora')
        self.assertContains(res_all, 'Carlinhos Sabino')

        res_mentor = self.client.get(reverse('profile_search'), {'role': 'mentor'})
        self.assertEqual(res_mentor.status_code, 200)
        self.assertContains(res_mentor, 'Ana Mentora')
        self.assertNotContains(res_mentor, 'Carlinhos Sabino')

        res_query = self.client.get(reverse('profile_search'), {'q': 'Arquitetura'})
        self.assertEqual(res_query.status_code, 200)
        self.assertContains(res_query, 'Ana Mentora')

    def test_public_profile_view(self):
        self.client.force_login(self.student)
        res = self.client.get(reverse('public_profile', kwargs={'user_id': self.mentor.id}))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Ana Mentora')
        self.assertContains(res, 'Python, Django &amp; Arquitetura')

    def test_dm_inbox_and_thread_conversation(self):
        from .models import DirectMessage
        self.client.force_login(self.student)

        # Enviar DM para a mentora
        thread_url = reverse('dm_thread', kwargs={'user_id': self.mentor.id})
        post_res = self.client.post(thread_url, {
            'content': 'Olá Mentora Ana! Pode me ajudar no desafio de List Comprehension?'
        })
        self.assertEqual(post_res.status_code, 302)
        self.assertTrue(DirectMessage.objects.filter(
            sender=self.student,
            recipient=self.mentor,
            content__icontains='List Comprehension'
        ).exists())

        # Verificar se aparece na caixa de entrada (dm_inbox)
        inbox_res = self.client.get(reverse('dm_inbox'))
        self.assertEqual(inbox_res.status_code, 200)
        self.assertContains(inbox_res, 'Ana Mentora')
        self.assertContains(inbox_res, 'List Comprehension')

    def test_sending_dm_triggers_notification_for_recipient(self):
        """Onda 6 (#26): Notificação de mensagem recebida"""
        from .models import Notification
        self.client.force_login(self.student)
        thread_url = reverse('dm_thread', kwargs={'user_id': self.mentor.id})
        self.client.post(thread_url, {'content': 'Olá Mentora! Dúvida técnica aqui.'})

        notif = Notification.objects.filter(user=self.mentor, title__icontains='Nova mensagem').first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.icon, '💬')
        self.assertIn('Carlinhos', notif.title)
        self.assertIn('Dúvida técnica aqui', notif.message)


class NotificationBellTests(TestCase):
    """
    Testes da Onda 5:
    Item #23: Alerta (sininho) de novas publicações e conquistas.
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='bell_user@codeview.com',
            password='Password123!',
            first_name='Dev Alerta'
        )
        from .models import Notification
        self.n1 = Notification.objects.create(
            user=self.user,
            title='Alerta 1',
            message='Primeira mensagem de teste.',
            icon='🔔',
            is_read=False
        )
        self.n2 = Notification.objects.create(
            user=self.user,
            title='Alerta 2',
            message='Segunda mensagem de teste.',
            icon='🚀',
            is_read=False
        )

    def test_notification_list_view_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/notifications.html')
        self.assertContains(response, 'Alerta 1')
        self.assertContains(response, 'Alerta 2')

    def test_mark_single_notification_read(self):
        self.client.force_login(self.user)
        url = reverse('notification_read', kwargs={'notification_id': self.n1.id})
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['unread_count'], 1)

        self.n1.refresh_from_db()
        self.assertTrue(self.n1.is_read)

    def test_mark_all_notifications_read(self):
        self.client.force_login(self.user)
        url = reverse('notifications_read_all')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.n1.refresh_from_db()
        self.n2.refresh_from_db()
        self.assertTrue(self.n1.is_read)
        self.assertTrue(self.n2.is_read)

    def test_notifications_context_processor(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['unread_notifications_count'], 2)


class TAMEvaluationTests(TestCase):
    """
    Testes do instrumento empírico de Aceitação de Tecnologia (TAM - Davis, 1989).
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='evaluator@codeview.com',
            password='Password123!',
            first_name='Avaliador Teste'
        )
        self.tam_url = reverse('tam_evaluation')

    def test_tam_get_view_renders_properly(self):
        response = self.client.get(self.tam_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/tam_evaluation.html')
        self.assertContains(response, 'Formulário de Aceitação de Tecnologia')
        self.assertContains(response, 'PU1: Pílulas Curtas')
        self.assertContains(response, 'PEOU1: Navegação Intuitiva')

    def test_tam_submit_anonymous_success(self):
        from accounts.models import TAMEvaluation
        payload = {
            'evaluator_name': 'Dev Externo',
            'evaluator_email': 'dev.externo@empresa.com',
            'role': 'dev_junior',
            'experience': '1_a_3_anos',
            'device': 'desktop',
            'pu1': 5, 'pu2': 5, 'pu3': 4, 'pu4': 4, 'pu5': 5,
            'peou1': 5, 'peou2': 4, 'peou3': 5, 'peou4': 4, 'peou5': 5,
            'atu1': 5, 'atu2': 5, 'atu3': 5,
            'biu1': 4, 'biu2': 5, 'biu3': 5,
            'highlights': 'Muito prático e direto ao ponto.',
            'difficulties': 'Nenhuma.',
            'suggestions': 'Mais trilhas de cloud.'
        }
        response = self.client.post(self.tam_url, data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/tam_success.html')

        eval_obj = TAMEvaluation.objects.get(evaluator_email='dev.externo@empresa.com')
        self.assertEqual(eval_obj.role, 'dev_junior')
        self.assertEqual(eval_obj.pu_score, 4.6)
        self.assertEqual(eval_obj.peou_score, 4.6)
        self.assertEqual(eval_obj.atu_score, 5.0)
        self.assertAlmostEqual(eval_obj.overall_score, 4.7166, places=2)

    def test_tam_submit_authenticated_links_user(self):
        from accounts.models import TAMEvaluation
        self.client.force_login(self.user)
        payload = {
            'role': 'estudante',
            'experience': 'menos_1_ano',
            'device': 'mobile',
            'pu1': 4, 'pu2': 4, 'pu3': 4, 'pu4': 4, 'pu5': 4,
            'peou1': 4, 'peou2': 4, 'peou3': 4, 'peou4': 4, 'peou5': 4,
            'atu1': 4, 'atu2': 4, 'atu3': 4,
            'biu1': 4, 'biu2': 4, 'biu3': 4,
        }
        response = self.client.post(self.tam_url, data=payload)
        self.assertEqual(response.status_code, 200)

        eval_obj = TAMEvaluation.objects.get(user=self.user)
        self.assertEqual(eval_obj.overall_score, 4.0)


class Onda8PortfolioAndLGPDTests(TestCase):
    """
    Testes de integração para a Onda 8:
    - Compartilhar perfil & Open Graph (#32)
    - Encerrar conta LGPD Art. 18 (#33)
    - Medidor de conhecimento técnico (#35)
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='portfolio.dev@codeview.com',
            password='Password123!',
            first_name='Dev',
            last_name='Portfolio'
        )
        from videos.models import Technology
        self.tech = Technology.objects.create(name='Python', slug='python', icon_name='🐍')

    def test_share_profile_metadata_and_open_graph(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse('profile'))
        self.assertEqual(res.status_code, 200)
        self.assertIn('absolute_profile_url', res.context)
        self.assertIn('tech_stats', res.context)
        self.assertIn('overall_rank', res.context)
        self.assertContains(res, 'og:title')
        self.assertContains(res, 'og:description')
        self.assertContains(res, 'Portfólio Vivo')
        self.assertContains(res, 'Compartilhe seu Portfólio Vivo')
        self.assertContains(res, 'Copiar')

    def test_public_profile_share_metadata(self):
        self.client.force_login(self.user)
        url = reverse('public_profile', kwargs={'user_id': self.user.id})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertIn('absolute_profile_url', res.context)
        self.assertContains(res, 'og:title')
        self.assertContains(res, 'Compartilhe este Portfólio Vivo')

    def test_knowledge_meter_calculation_and_rank_progression(self):
        from courses.models import Course, Lesson, Challenge, ChallengeAttempt, Certificate

        # Rank inicial: Estudante Praticante
        self.client.force_login(self.user)
        res1 = self.client.get(reverse('profile'))
        self.assertEqual(res1.context['overall_rank'], 'Estudante Praticante • Iniciante')

        # Criar curso, aula e desafio resolvido (+50 pontos)
        course = Course.objects.create(
            title='Python Prático',
            slug='python-pratico',
            description='Curso prático de Python',
            technology=self.tech,
            instructor=self.user,
            is_published=True
        )
        lesson = Lesson.objects.create(
            course=course,
            title='List Comprehensions',
            order=1,
            duration_seconds=60
        )
        challenge = Challenge.objects.create(
            lesson=lesson,
            title='Filtro de Pares',
            question_text='Como filtrar números pares em Python?',
            option_a='[x for x in r if x % 2 == 0]',
            option_b='filter(lambda x: x)',
            option_c='pares()',
            correct_option='A',
            explanation='List comprehension com condicional if filtra corretamente.',
            points=50
        )
        ChallengeAttempt.objects.create(
            user=self.user,
            challenge=challenge,
            submitted_code='pares = [x for x in range(10) if x % 2 == 0]',
            is_correct=True
        )

        res2 = self.client.get(reverse('profile'))
        self.assertEqual(res2.context['challenges_solved_count'], 1)
        self.assertEqual(res2.context['total_points'], 50)
        self.assertEqual(res2.context['overall_rank'], 'Junior Developer • Em Ascensão')

        # Emitir certificado -> Deve elevar para Pleno
        Certificate.objects.create(
            user=self.user,
            course=course,
            validation_code='CERT-TEST-ONDA8'
        )

        res3 = self.client.get(reverse('profile'))
        self.assertEqual(res3.context['overall_rank'], 'Pleno Developer • Autônomo')

        # Verificar se os dados de tech_stats foram computados
        tech_stat = next((t for t in res3.context['tech_stats'] if t['tech'].slug == 'python'), None)
        self.assertIsNotNone(tech_stat)
        self.assertEqual(tech_stat['solved_count'], 1)
        self.assertEqual(tech_stat['certs_count'], 1)
        self.assertTrue(tech_stat['has_activity'])
        self.assertGreater(tech_stat['percentage'], 0)

    def test_account_delete_view_lgpd_requires_login(self):
        delete_url = reverse('account_delete')
        res = self.client.get(delete_url)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/accounts/login/', res.url)

    def test_account_delete_view_lgpd_rejection_on_invalid_credentials(self):
        self.client.force_login(self.user)
        delete_url = reverse('account_delete')
        res = self.client.post(delete_url, {'password': 'WrongPassword123'})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_account_delete_view_lgpd_success_with_password(self):
        user_id = self.user.id
        self.client.force_login(self.user)
        delete_url = reverse('account_delete')
        res = self.client.post(delete_url, {'password': 'Password123!'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('login'))
        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertFalse(Profile.objects.filter(user_id=user_id).exists())

    def test_account_delete_view_lgpd_success_with_keyword(self):
        user2 = User.objects.create_user(
            email='delete.me@codeview.com',
            password='Password123!',
            first_name='Para',
            last_name='Deletar'
        )
        user2_id = user2.id
        self.client.force_login(user2)
        delete_url = reverse('account_delete')
        res = self.client.post(delete_url, {'confirm_keyword': 'DELETAR'})
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('login'))
        self.assertFalse(User.objects.filter(id=user2_id).exists())


class AdminDashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.regular_user = User.objects.create_user(
            email='user@codeview.com',
            password='Password123!',
            first_name='Dev'
        )
        self.admin_user = User.objects.create_superuser(
            email='admin@codeview.com',
            password='Password123!',
            first_name='SuperAdmin'
        )
        self.url = reverse('admin_dashboard')

    def test_admin_dashboard_anonymous_redirects_to_login(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse('login'), res.url)

    def test_admin_dashboard_regular_user_forbidden_and_redirects(self):
        self.client.force_login(self.regular_user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('feed'))

    def test_admin_dashboard_superuser_access_ok(self):
        from accounts.models import TAMEvaluation
        from videos.models import Technology
        
        Technology.objects.create(name='Python Test', icon_name='🐍', is_active=True)
        TAMEvaluation.objects.create(
            user=self.admin_user,
            device='desktop',
            role='dev_junior',
            experience='1_a_3_anos',
            pu1=5, pu2=5, pu3=5, pu4=5, pu5=5,
            peou1=4, peou2=4, peou3=4, peou4=4, peou5=4,
            atu1=5, atu2=5, atu3=5,
            biu1=5, biu2=5, biu3=5,
            highlights='Agilidade nas aulas',
            difficulties='Nenhuma',
            suggestions='Adicionar mais cursos'
        )
        self.client.force_login(self.admin_user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Painel do Super Administrador')
        self.assertContains(res, 'Python Test')
        self.assertContains(res, 'Agilidade nas aulas')
        self.assertEqual(res.context['total_tam'], 1)
        self.assertIn('chart_tam_labels_json', res.context)
        self.assertIn('roles_analytics', res.context)
        self.assertIn('roles_analytics_json', res.context)
        self.assertIn('chart_roles_scores_data_json', res.context)
        self.assertEqual(res.context['roles_analytics']['dev_junior']['count'], 1)
        self.assertEqual(res.context['roles_analytics']['estudante']['count'], 0)
        self.assertContains(res, 'Distribuição &amp; Avaliação por Perfil Profissional')
        self.assertContains(res, 'role-filter-buttons')
        self.assertContains(res, 'chartRolesScores')

    def test_admin_dashboard_create_technology(self):
        from videos.models import Technology
        self.client.force_login(self.admin_user)
        res = self.client.post(self.url, {
            'action': 'create_technology',
            'name': 'Golang',
            'icon_name': '🐹',
            'is_active': 'on'
        })
        self.assertEqual(res.status_code, 302)
        self.assertTrue(Technology.objects.filter(name='Golang').exists())
        tech = Technology.objects.get(name='Golang')
        self.assertEqual(tech.icon_name, '🐹')
        self.assertTrue(tech.is_active)

    def test_admin_dashboard_toggle_technology(self):
        from videos.models import Technology
        tech = Technology.objects.create(name='Rust', icon_name='🦀', is_active=True)
        self.client.force_login(self.admin_user)
        res = self.client.post(self.url, {
            'action': 'toggle_technology',
            'technology_id': tech.id
        })
        self.assertEqual(res.status_code, 302)
        tech.refresh_from_db()
        self.assertFalse(tech.is_active)

    def test_admin_dashboard_delete_technology(self):
        from videos.models import Technology
        tech = Technology.objects.create(name='Kotlin', icon_name='📱', is_active=True)
        self.client.force_login(self.admin_user)
        res = self.client.post(self.url, {
            'action': 'delete_technology',
            'technology_id': tech.id
        })
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Technology.objects.filter(id=tech.id).exists())


