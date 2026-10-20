from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError
from videos.models import Technology
from .models import Course, Lesson, Enrollment, Challenge, ChallengeAttempt

User = get_user_model()


class CourseModelTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            email='instructor@codeview.com',
            password='Password123!',
            first_name='Instrutor'
        )
        self.tech = Technology.objects.create(name='Python', slug='python', icon_name='🐍')

    def test_create_course_and_auto_slug(self):
        course = Course.objects.create(
            title='Python para Dados',
            description='Curso prático de análise de dados.',
            technology=self.tech,
            instructor=self.instructor,
            level='iniciante',
            estimated_minutes=40
        )
        self.assertEqual(course.slug, 'python-para-dados')
        self.assertEqual(str(course), 'Python para Dados [Python]')
        self.assertEqual(course.total_lessons, 0)
        self.assertTrue(course.is_published)


class LessonModelTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            email='instructor@codeview.com',
            password='Password123!',
            first_name='Instrutor'
        )
        self.course = Course.objects.create(
            title='FastAPI Básico',
            description='APIs modernas com Python.',
            instructor=self.instructor
        )

    def test_create_lesson(self):
        lesson = Lesson.objects.create(
            course=self.course,
            title='Instalação e Hello World',
            order=1,
            duration_seconds=90
        )
        self.assertEqual(str(lesson), 'FastAPI Básico - Aula 1: Instalação e Hello World')
        self.assertEqual(self.course.total_lessons, 1)


class EnrollmentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='student@codeview.com',
            password='Password123!',
            first_name='Aluno'
        )
        self.course = Course.objects.create(
            title='Django Rápido',
            description='Web com Django.',
            instructor=self.user
        )

    def test_create_enrollment(self):
        enrollment = Enrollment.objects.create(user=self.user, course=self.course)
        self.assertTrue(enrollment.is_active)
        self.assertFalse(enrollment.is_completed)
        self.assertIn(self.user.email, str(enrollment))

    def test_unique_enrollment_per_user_and_course(self):
        Enrollment.objects.create(user=self.user, course=self.course)
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(user=self.user, course=self.course)


class CourseViewsIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            email='carlinhos@codeview.com',
            password='Password123!',
            first_name='Carlinhos'
        )
        self.instructor = User.objects.create_user(
            email='prof@codeview.com',
            password='Password123!',
            first_name='Professor'
        )
        self.tech_python = Technology.objects.create(name='Python', slug='python', icon_name='🐍')
        self.tech_js = Technology.objects.create(name='JavaScript', slug='javascript', icon_name='⚡')

        self.course_python = Course.objects.create(
            title='Automação Python',
            description='Scripts úteis em Python.',
            technology=self.tech_python,
            instructor=self.instructor,
            level='iniciante',
            is_published=True
        )
        self.lesson_python = Lesson.objects.create(
            course=self.course_python,
            title='Primeira Automação',
            order=1
        )

        self.course_js = Course.objects.create(
            title='JavaScript Intermediário',
            description='Aprofunde em JS.',
            technology=self.tech_js,
            instructor=self.instructor,
            level='intermediario',
            is_published=True
        )

    def test_course_list_view_public(self):
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course_list.html')
        self.assertContains(response, 'Automação Python')
        self.assertContains(response, 'JavaScript Intermediário')

    def test_course_list_filter_by_tech(self):
        response = self.client.get(reverse('course_list'), {'tech': 'python'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Automação Python')
        self.assertNotContains(response, 'JavaScript Intermediário')

    def test_course_list_filter_by_level(self):
        response = self.client.get(reverse('course_list'), {'level': 'intermediario'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Automação Python')
        self.assertContains(response, 'JavaScript Intermediário')

    def test_course_list_search_query(self):
        response = self.client.get(reverse('course_list'), {'q': 'Scripts úteis'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Automação Python')
        self.assertNotContains(response, 'JavaScript Intermediário')

    def test_course_detail_view(self):
        response = self.client.get(reverse('course_detail', kwargs={'slug': self.course_python.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course_detail.html')
        self.assertContains(response, 'Automação Python')
        self.assertContains(response, 'Primeira Automação')
        self.assertFalse(response.context['is_enrolled'])

    def test_enroll_requires_login(self):
        response = self.client.post(reverse('course_enroll', kwargs={'slug': self.course_python.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_enroll_authenticated_success(self):
        self.client.login(email='carlinhos@codeview.com', password='Password123!')
        response = self.client.post(reverse('course_enroll', kwargs={'slug': self.course_python.slug}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Enrollment.objects.filter(user=self.student, course=self.course_python, is_active=True).exists())

    def test_unenroll_authenticated_success(self):
        Enrollment.objects.create(user=self.student, course=self.course_python, is_active=True)
        self.client.login(email='carlinhos@codeview.com', password='Password123!')
        response = self.client.post(reverse('course_unenroll', kwargs={'slug': self.course_python.slug}))
        self.assertEqual(response.status_code, 302)
        enrollment = Enrollment.objects.get(user=self.student, course=self.course_python)
        self.assertFalse(enrollment.is_active)


class SeedCoursesCommandTest(TestCase):
    def test_seed_courses_command(self):
        call_command('seed_courses')
        self.assertGreaterEqual(Course.objects.count(), 3)
        self.assertGreaterEqual(Lesson.objects.count(), 6)
        self.assertGreaterEqual(Challenge.objects.count(), 3)


class ChallengeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='prof_c@codeview.com', password='Pass12345!', first_name='Prof')
        self.course = Course.objects.create(title='Python Pro', description='Desc', instructor=self.user)
        self.lesson = Lesson.objects.create(course=self.course, title='Aula 1', order=1)

    def test_create_challenge(self):
        ch = Challenge.objects.create(
            lesson=self.lesson,
            title='Desafio Sintaxe',
            question_text='Qual a sintaxe correta?',
            option_a='print("ok")',
            option_b='echo "ok"',
            option_c='puts "ok"',
            correct_option='A',
            explanation='Python usa print().',
            points=15
        )
        self.assertEqual(str(ch), 'Desafio: Desafio Sintaxe (Python Pro)')
        self.assertEqual(ch.points, 15)
        self.assertEqual(ch.correct_option, 'A')


class ChallengeViewIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='aluno_c@codeview.com', password='Pass12345!', first_name='Aluno')
        self.course = Course.objects.create(title='Python Básico', description='Desc', instructor=self.user)
        self.lesson1 = Lesson.objects.create(course=self.course, title='Aula 1', order=1)
        self.lesson2 = Lesson.objects.create(course=self.course, title='Aula 2', order=2)

        self.challenge = Challenge.objects.create(
            lesson=self.lesson1,
            title='Desafio List Comp',
            question_text='Qual retorna pares?',
            code_snippet='numeros = [1, 2, 3, 4]',
            option_a='[x for x in numeros if x % 2 == 0]',
            option_b='[x if x % 2 == 0]',
            option_c='numeros.filter()',
            correct_option='A',
            explanation='A cláusula if vai ao final.',
            points=20
        )

    def test_challenge_requires_login(self):
        url = reverse('lesson_challenge', kwargs={'lesson_id': self.lesson1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_challenge_view_get_authenticated(self):
        self.client.login(email='aluno_c@codeview.com', password='Pass12345!')
        url = reverse('lesson_challenge', kwargs={'lesson_id': self.lesson1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/challenge.html')
        self.assertContains(response, 'Desafio List Comp')
        self.assertContains(response, 'numeros = [1, 2, 3, 4]')
        self.assertContains(response, '+20 pontos')

    def test_challenge_submit_wrong_answer_ajax(self):
        self.client.login(email='aluno_c@codeview.com', password='Pass12345!')
        url = reverse('lesson_challenge', kwargs={'lesson_id': self.lesson1.id})
        response = self.client.post(
            url,
            data='{"selected_option": "B"}',
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['status'], 'success')
        self.assertFalse(json_data['is_correct'])
        self.assertEqual(json_data['points'], 0)

        attempt = ChallengeAttempt.objects.get(user=self.user, challenge=self.challenge)
        self.assertFalse(attempt.is_correct)
        self.assertEqual(attempt.selected_option, 'B')

    def test_challenge_submit_correct_answer_ajax(self):
        self.client.login(email='aluno_c@codeview.com', password='Pass12345!')
        url = reverse('lesson_challenge', kwargs={'lesson_id': self.lesson1.id})
        response = self.client.post(
            url,
            data='{"selected_option": "A"}',
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['status'], 'success')
        self.assertTrue(json_data['is_correct'])
        self.assertEqual(json_data['points'], 20)
        self.assertIn('A cláusula if vai ao final.', json_data['explanation'])

        attempt = ChallengeAttempt.objects.get(user=self.user, challenge=self.challenge)
        self.assertTrue(attempt.is_correct)
        self.assertEqual(attempt.selected_option, 'A')

    def test_challenge_code_submission_and_auto_lesson_progress(self):
        from .models import LessonProgress
        self.client.force_login(self.user)
        url = reverse('lesson_challenge', kwargs={'lesson_id': self.lesson1.id})
        response = self.client.post(
            url,
            data='{"selected_option": "A", "submitted_code": "pares = [x for x in numeros if x % 2 == 0]"}',
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertTrue(json_data['is_correct'])
        self.assertIn('pares =', json_data['submitted_code'])
        self.assertTrue(LessonProgress.objects.filter(user=self.user, lesson=self.lesson1, is_completed=True).exists())


class CourseProgressAndCertificateTests(TestCase):
    """
    Testes da Onda 4: Progresso do curso (LessonProgress) e Emissão do Certificado Digital (Certificate).
    """
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            email='cert_student@codeview.com',
            password='Pass12345!',
            first_name='Karol',
            last_name='Sabino'
        )
        self.instructor = User.objects.create_user(
            email='cert_mentor@codeview.com',
            password='Pass12345!',
            first_name='Mentor'
        )
        self.course = Course.objects.create(
            title='Trilha Certificada Python',
            description='Curso com certificado.',
            instructor=self.instructor,
            is_published=True
        )
        self.lesson1 = Lesson.objects.create(course=self.course, title='Aula 1', order=1)
        self.lesson2 = Lesson.objects.create(course=self.course, title='Aula 2', order=2)

    def test_course_progress_and_certificate_issuance(self):
        from .models import Certificate
        self.client.force_login(self.student)

        # Tentar emitir certificado antes de concluir 100% deve bloquear
        res_early = self.client.post(reverse('issue_certificate', kwargs={'slug': self.course.slug}))
        self.assertEqual(res_early.status_code, 302)
        self.assertFalse(Certificate.objects.filter(user=self.student, course=self.course).exists())

        # Concluir Aula 1 (50%)
        self.client.post(reverse('lesson_complete', kwargs={'lesson_id': self.lesson1.id}))
        comp, tot, pct = self.course.get_user_progress(self.student)
        self.assertEqual((comp, tot, pct), (1, 2, 50))

        # Concluir Aula 2 (100%)
        self.client.post(reverse('lesson_complete', kwargs={'lesson_id': self.lesson2.id}))
        comp, tot, pct = self.course.get_user_progress(self.student)
        self.assertEqual((comp, tot, pct), (2, 2, 100))

        # Emitir Certificado com 100% concluído
        res_cert = self.client.post(reverse('issue_certificate', kwargs={'slug': self.course.slug}))
        self.assertEqual(res_cert.status_code, 302)
        cert = Certificate.objects.filter(user=self.student, course=self.course).first()
        self.assertIsNotNone(cert)
        self.assertTrue(cert.validation_code.startswith('CV-2026-'))

        # Visualizar página pública do Certificado Digital
        res_detail = self.client.get(reverse('certificate_detail', kwargs={'validation_code': cert.validation_code}))
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, 'Karol Sabino')
        self.assertContains(res_detail, 'Trilha Certificada Python')
        self.assertContains(res_detail, cert.validation_code)



class CertificateDownloadAndQrTests(TestCase):
    """
    Testes da Onda 5:
    Item #20: Baixar certificado (PDF).
    Item #21: Compartilhar certificado (QR Code público).
    """
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            email='cert_download@codeview.com',
            password='Pass12345!',
            first_name='Mariana',
            last_name='Dev'
        )
        self.instructor = User.objects.create_user(
            email='mentor_pdf@codeview.com',
            password='Pass12345!',
            first_name='Instrutor Rodrigo'
        )
        self.tech = Technology.objects.create(name='Django', slug='django', icon_name='🎯')
        self.course = Course.objects.create(
            title='Django Rest Framework Avançado',
            slug='drf-avancado',
            description='APIs profissionais.',
            technology=self.tech,
            instructor=self.instructor,
            is_published=True
        )
        from .models import Certificate
        self.certificate = Certificate.objects.create(
            user=self.student,
            course=self.course,
            validation_code='CV-2026-DRFTEST1'
        )

    def test_certificate_qr_code_view_returns_png_image(self):
        url = reverse('certificate_qr', kwargs={'validation_code': self.certificate.validation_code})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertGreater(len(response.content), 100)

    def test_download_certificate_pdf_view_returns_pdf(self):
        url = reverse('certificate_pdf', kwargs={'validation_code': self.certificate.validation_code})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertIn('CV-2026-DRFTEST1.pdf', response['Content-Disposition'])
        self.assertGreater(len(response.content), 500)

    def test_certificate_issuance_triggers_notification(self):
        from accounts.models import Notification
        new_course = Course.objects.create(
            title='Nova Trilha Fullstack',
            slug='nova-trilha-fullstack',
            description='Curso completo.',
            instructor=self.instructor,
            is_published=True
        )
        l1 = Lesson.objects.create(course=new_course, title='Aula Única', order=1)
        self.client.force_login(self.student)
        self.client.post(reverse('lesson_complete', kwargs={'lesson_id': l1.id}))

        # Emitir
        self.client.post(reverse('issue_certificate', kwargs={'slug': new_course.slug}))

        notif = Notification.objects.filter(user=self.student, title__icontains='Certificado Emitido').first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.icon, '🎓')
        self.assertIn('Nova Trilha Fullstack', notif.message)
