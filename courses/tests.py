from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError
from videos.models import Technology
from .models import Course, Lesson, Enrollment

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
