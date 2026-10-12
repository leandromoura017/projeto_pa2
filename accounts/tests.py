from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
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
        # Verifica se o consentimento LGPD foi registrado
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
        # O usuário deve estar autenticado na sessão do client
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


import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


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

