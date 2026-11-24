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


class Onda6CourseFeaturesTests(TestCase):
    """
    Testes da Onda 6:
    Item #25: Cronograma do curso (schedule_stages na view de detalhes).
    Item #27: Notificações de inscrição confirmada.
    """
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            email='aluno_onda6@codeview.com',
            password='Pass12345!',
            first_name='Aluno Onda 6'
        )
        self.instructor = User.objects.create_user(
            email='prof_onda6@codeview.com',
            password='Pass12345!',
            first_name='Instrutor Onda 6'
        )
        self.course = Course.objects.create(
            title='Docker e Containers',
            slug='docker-e-containers',
            description='Domine Docker em pílulas.',
            instructor=self.instructor,
            is_published=True
        )
        self.lesson1 = Lesson.objects.create(course=self.course, title='Introdução Docker', order=1)
        self.lesson2 = Lesson.objects.create(course=self.course, title='Dockerfile e Imagens', order=2)
        self.lesson3 = Lesson.objects.create(course=self.course, title='Docker Compose e Redes', order=3)

    def test_course_detail_includes_schedule_stages(self):
        response = self.client.get(reverse('course_detail', kwargs={'slug': self.course.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('schedule_stages', response.context)
        stages = response.context['schedule_stages']
        self.assertGreater(len(stages), 0)
        self.assertTrue(all(stage['status'] == 'pending' for stage in stages))
        self.assertContains(response, 'Cronograma de Estudos Sugerido')

    def test_course_detail_schedule_stages_dynamic_progress(self):
        from courses.models import LessonProgress
        self.client.force_login(self.student)

        LessonProgress.objects.create(user=self.student, lesson=self.lesson1, is_completed=True)
        response = self.client.get(reverse('course_detail', kwargs={'slug': self.course.slug}))
        self.assertEqual(response.status_code, 200)
        stages = response.context['schedule_stages']
        self.assertEqual(stages[0]['completed_lessons'], 1)

    def test_enrollment_triggers_notification(self):
        from accounts.models import Notification
        self.client.force_login(self.student)
        response = self.client.post(reverse('course_enroll', kwargs={'slug': self.course.slug}))
        self.assertEqual(response.status_code, 302)

        notif = Notification.objects.filter(user=self.student, title__icontains='Inscrição Confirmada').first()
        self.assertIsNotNone(notif)
        self.assertIn('Docker e Containers', notif.message)
        self.assertEqual(notif.icon, '🚀')


class Onda7CourseFeaturesTests(TestCase):
    """
    Testes da Onda 7:
    Item #30: Aba de cadastrar cursos (course_create_view).
    Item #31: Notificações de inscrição cancelada (unenroll_course_view).
    """
    def setUp(self):
        self.client = Client()
        self.mentor = User.objects.create_user(
            email='mentor_onda7@codeview.com',
            password='Pass12345!',
            first_name='Mentor Onda 7'
        )
        self.student = User.objects.create_user(
            email='student_onda7@codeview.com',
            password='Pass12345!',
            first_name='Aluno Onda 7'
        )
        self.tech = Technology.objects.create(name='Rust', slug='rust', icon_name='🦀')
        self.course = Course.objects.create(
            title='Rust para Iniciantes',
            slug='rust-para-iniciantes',
            description='Ownership e Borrowing na prática.',
            technology=self.tech,
            instructor=self.mentor,
            is_published=True
        )

    def test_course_create_view_get(self):
        self.client.force_login(self.mentor)
        response = self.client.get(reverse('course_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course_create.html')
        self.assertContains(response, 'Cadastrar Novo')

    def test_course_create_view_post_success(self):
        from accounts.models import Notification
        self.client.force_login(self.mentor)

        payload = {
            'title': 'Arquitetura de Microsserviços com Go',
            'description': 'Construa serviços distribuídos e escaláveis em pílulas.',
            'technology': self.tech.id,
            'level': 'avancado',
            'estimated_minutes': '50',
        }
        response = self.client.post(reverse('course_create'), data=payload)
        self.assertEqual(response.status_code, 302)

        created_course = Course.objects.filter(title='Arquitetura de Microsserviços com Go').first()
        self.assertIsNotNone(created_course)
        self.assertEqual(created_course.slug, 'arquitetura-de-microsservicos-com-go')
        self.assertEqual(created_course.level, 'avancado')
        self.assertEqual(created_course.estimated_minutes, 50)
        self.assertEqual(created_course.instructor, self.mentor)

        # Disparo de notificação para o criador da trilha
        notif = Notification.objects.filter(user=self.mentor, title__icontains='Nova Trilha Criada').first()
        self.assertIsNotNone(notif)
        self.assertIn('Arquitetura de Microsserviços com Go', notif.message)
        self.assertEqual(notif.icon, '🚀')

    def test_unenroll_triggers_cancellation_notification(self):
        from accounts.models import Notification
        Enrollment.objects.create(user=self.student, course=self.course, is_active=True)

        self.client.force_login(self.student)
        url = reverse('course_unenroll', kwargs={'slug': self.course.slug})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        enrollment = Enrollment.objects.get(user=self.student, course=self.course)
        self.assertFalse(enrollment.is_active)

        notif = Notification.objects.filter(user=self.student, title__icontains='Matrícula Cancelada').first()
        self.assertIsNotNone(notif)
        self.assertIn('Rust para Iniciantes', notif.message)
        self.assertEqual(notif.icon, '⚠️')


class DynamicCourseCreatorTests(TestCase):
    """
    Testes para criação dinâmica de cursos, gestão de aulas, upload de vídeos,
    cronograma customizado e cadastro de mini-atividades pelo criador de conteúdo.
    """
    def setUp(self):
        self.client = Client()
        self.creator = User.objects.create_user(
            email='creator_dynamic@codeview.com',
            password='Password123!',
            first_name='Criador Dinamico'
        )
        self.other_user = User.objects.create_user(
            email='other_user@codeview.com',
            password='Password123!',
            first_name='Outro Usuario'
        )
        self.tech = Technology.objects.create(name='Python', slug='python', icon_name='🐍')
        self.client.force_login(self.creator)

    def test_create_course_with_custom_schedule(self):
        """Qualquer perfil pode criar curso com cronograma personalizado."""
        payload = {
            'title': 'Engenharia de Dados Prática',
            'technology': self.tech.id,
            'description': 'Pipeline de dados em tempo real com Python.',
            'level': 'intermediario',
            'estimated_minutes': 90,
            'custom_schedule': 'Dia 1: Ingestão de dados\nDia 2: Transformação com Pandas\nDia 3: Carga e testes',
        }
        res = self.client.post(reverse('course_create'), data=payload)
        self.assertEqual(res.status_code, 302)

        course = Course.objects.filter(title='Engenharia de Dados Prática').first()
        self.assertIsNotNone(course)
        self.assertEqual(course.instructor, self.creator)
        self.assertIn('Dia 1: Ingestão de dados', course.custom_schedule)
        # Verifica se o perfil foi atualizado para is_mentor
        self.creator.profile.refresh_from_db()
        self.assertTrue(self.creator.profile.is_mentor)

    def test_course_manage_view_access_permissions(self):
        """Apenas o criador ou superusuário pode acessar o gerenciamento do curso."""
        course = Course.objects.create(
            title='Docker do Zero',
            slug='docker-do-zero',
            description='Curso de containers',
            technology=self.tech,
            instructor=self.creator
        )
        # Criador acessa com 200
        res = self.client.get(reverse('course_manage', kwargs={'slug': course.slug}))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'courses/course_manage.html')

        # Outro usuário é barrado com redirect
        self.client.force_login(self.other_user)
        res_other = self.client.get(reverse('course_manage', kwargs={'slug': course.slug}))
        self.assertEqual(res_other.status_code, 302)

    def test_lesson_create_with_video_and_challenge(self):
        """Criador adiciona nova aula com upload de vídeo e desafio prático na mesma trilha."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        course = Course.objects.create(
            title='FastAPI Moderno',
            slug='fastapi-moderno',
            description='APIs assíncronas',
            technology=self.tech,
            instructor=self.creator
        )

        fake_video = SimpleUploadedFile('aula1.mp4', b'fake-mp4-data', content_type='video/mp4')
        payload = {
            'title': 'Aula 1: Primeiro Endpoint com FastAPI',
            'order': 1,
            'duration_seconds': 90,
            'content': 'Explicação da rota @app.get("/")',
            'video_file': fake_video,
            # Dados da mini-atividade / desafio
            'challenge_title': 'Desafio: Retorno de Status Code',
            'question_text': 'Qual o decorator correto para criar uma rota GET?',
            'option_a': '@app.get("/")',
            'option_b': '@app.post("/")',
            'option_c': '@app.route("/")',
            'option_d': '@app.view("/")',
            'correct_option': 'A',
            'points': 15,
        }
        res = self.client.post(reverse('lesson_create', kwargs={'slug': course.slug}), data=payload)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse('course_manage', kwargs={'slug': course.slug}))

        lesson = Lesson.objects.filter(course=course, title='Aula 1: Primeiro Endpoint com FastAPI').first()
        self.assertIsNotNone(lesson)
        self.assertIsNotNone(lesson.video)
        self.assertEqual(lesson.duration_seconds, 90)

        # Desafio criado e vinculado à aula
        self.assertIsNotNone(lesson.challenge)
        self.assertEqual(lesson.challenge.title, 'Desafio: Retorno de Status Code')
        self.assertEqual(lesson.challenge.correct_option, 'A')
        self.assertEqual(lesson.challenge.points, 15)

    def test_lesson_create_rejects_image_file(self):
        """Tentativa de subir imagem como vídeo da aula deve ser rejeitada."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        course = Course.objects.create(
            title='Django Security',
            slug='django-security',
            description='Segurança web',
            technology=self.tech,
            instructor=self.creator
        )

        fake_png = SimpleUploadedFile('foto.png', b'fake-png-data', content_type='image/png')
        payload = {
            'title': 'Aula com Imagem Inválida',
            'order': 1,
            'duration_seconds': 60,
            'content': 'Teste',
            'video_file': fake_png,
        }
        res = self.client.post(reverse('lesson_create', kwargs={'slug': course.slug}), data=payload)
        self.assertEqual(res.status_code, 200) # Permanece no form com erro
        self.assertFalse(Lesson.objects.filter(course=course, title='Aula com Imagem Inválida').exists())

    def test_lesson_edit_and_delete(self):
        """Criador pode editar e excluir aulas da sua trilha com reordenação automática."""
        course = Course.objects.create(
            title='Trilha com Aulas',
            slug='trilha-com-aulas',
            description='Curso',
            technology=self.tech,
            instructor=self.creator
        )
        l1 = Lesson.objects.create(course=course, title='Aula 1', order=1, duration_seconds=60)
        l2 = Lesson.objects.create(course=course, title='Aula 2', order=2, duration_seconds=60)

        # Edição
        edit_payload = {
            'title': 'Aula 1 Modificada',
            'order': 1,
            'duration_seconds': 120,
            'content': 'Novo conteúdo complementar',
        }
        res_edit = self.client.post(reverse('lesson_edit', kwargs={'slug': course.slug, 'lesson_id': l1.id}), data=edit_payload)
        self.assertEqual(res_edit.status_code, 302)
        l1.refresh_from_db()
        self.assertEqual(l1.title, 'Aula 1 Modificada')
        self.assertEqual(l1.duration_seconds, 120)

        # Exclusão da Aula 1
        res_del = self.client.post(reverse('lesson_delete', kwargs={'slug': course.slug, 'lesson_id': l1.id}))
        self.assertEqual(res_del.status_code, 302)
        self.assertFalse(Lesson.objects.filter(id=l1.id).exists())

        # Aula 2 deve ser reordenada para order=1
        l2.refresh_from_db()
        self.assertEqual(l2.order, 1)

    def test_challenge_manage_create_and_update(self):
        """Criador pode cadastrar e editar mini-atividade interativa para qualquer aula."""
        course = Course.objects.create(
            title='Trilha Desafio',
            slug='trilha-desafio',
            description='Curso',
            technology=self.tech,
            instructor=self.creator
        )
        lesson = Lesson.objects.create(course=course, title='Aula Única', order=1)

        url = reverse('challenge_manage', kwargs={'slug': course.slug, 'lesson_id': lesson.id})
        payload = {
            'title': 'Qual a função de len() em Python?',
            'question_text': 'O que a função len() retorna?',
            'option_a': 'O tamanho/comprimento de um objeto',
            'option_b': 'O tipo do objeto',
            'option_c': 'Um número aleatório',
            'option_d': 'Um erro em listas vazias',
            'correct_option': 'A',
            'explanation': 'len() retorna a contagem de elementos.',
            'points': 20,
        }
        res = self.client.post(url, data=payload)
        self.assertEqual(res.status_code, 302)

        lesson.refresh_from_db()
        self.assertIsNotNone(lesson.challenge)
        self.assertEqual(lesson.challenge.correct_option, 'A')
        self.assertEqual(lesson.challenge.points, 20)

    def test_my_courses_view(self):
        """View meus-cursos deve listar os cursos criados pelo usuário logado."""
        Course.objects.create(
            title='Meu Curso 1',
            slug='meu-curso-1',
            description='Desc 1',
            technology=self.tech,
            instructor=self.creator
        )
        res = self.client.get(reverse('my_courses'))
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'courses/my_courses.html')
        self.assertContains(res, 'Meu Curso 1')



