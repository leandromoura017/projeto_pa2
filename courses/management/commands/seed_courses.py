from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from videos.models import Technology, Video
from courses.models import Course, Lesson

User = get_user_model()


class Command(BaseCommand):
    help = "Popula o banco de dados com mini-cursos e aulas iniciais para a Onda 2."

    def handle(self, *args, **options):
        # 1. Obter instrutor padrão (admin)
        instructor = User.objects.filter(is_superuser=True).first()
        if not instructor:
            instructor = User.objects.create_superuser('admin@codeview.com', 'admin12345', first_name='Admin')

        # 2. Obter Tecnologias
        tech_python = Technology.objects.filter(slug='python').first()
        tech_js = Technology.objects.filter(slug='javascript').first()
        tech_django = Technology.objects.filter(slug='django').first()

        video_python = Video.objects.filter(technology=tech_python).first()
        video_js = Video.objects.filter(technology=tech_js).first()
        video_django = Video.objects.filter(technology=tech_django).first()

        # 3. Criar Cursos
        courses_data = [
            {
                'title': 'Automação de Processos com Python',
                'slug': 'automacao-processos-python',
                'description': 'Aprenda a eliminar tarefas repetitivas e criar scripts rápidos de automação para o seu dia a dia e para a sua empresa.',
                'technology': tech_python,
                'level': 'iniciante',
                'estimated_minutes': 25,
                'lessons': [
                    {'title': 'Loops e List Comprehensions Eficientes', 'video': video_python, 'content': 'Transformando loops longos em sintaxe elegante de uma linha.', 'duration': 45},
                    {'title': 'Macetes de Dicionários e Tratamento de Erros', 'video': None, 'content': 'Como usar .get() para evitar crashes em rotinas de dados.', 'duration': 60},
                    {'title': 'Automatizando Leitura de Arquivos e Relatórios', 'video': None, 'content': 'Script prático para consolidar dados automaticamente.', 'duration': 90},
                ]
            },
            {
                'title': 'JavaScript Assíncrono Descomplicado',
                'slug': 'javascript-assincrono-descomplicado',
                'description': 'Domine Promises, Async/Await e o ciclo de eventos do JS para criar aplicações web fluidas sem travamento de tela.',
                'technology': tech_js,
                'level': 'intermediario',
                'estimated_minutes': 20,
                'lessons': [
                    {'title': 'Async / Await e Promessas sem Callback Hell', 'video': video_js, 'content': 'Entenda como o event loop do V8 processa chamadas assíncronas.', 'duration': 50},
                    {'title': 'Consumindo APIs REST com Fetch Moderno', 'video': None, 'content': 'Tratamento de status HTTP, headers e respostas JSON.', 'duration': 75},
                ]
            },
            {
                'title': 'Arquitetura Backend Ágil com Django',
                'slug': 'arquitetura-backend-agil-django',
                'description': 'Estruture projetos Django escaláveis desde o dia 1: autenticação limpa, models consistentes e performance no ORM.',
                'technology': tech_django,
                'level': 'intermediario',
                'estimated_minutes': 35,
                'lessons': [
                    {'title': 'Custom User Model sem dor de cabeça', 'video': video_django, 'content': 'Por que e como herdar de AbstractUser antes da primeira migração.', 'duration': 60},
                    {'title': 'Otimização de Queries com select_related', 'video': None, 'content': 'Eliminando o problema clássico de N+1 queries no Django.', 'duration': 80},
                ]
            }
        ]

        for c_data in courses_data:
            course, created = Course.objects.get_or_create(
                slug=c_data['slug'],
                defaults={
                    'title': c_data['title'],
                    'description': c_data['description'],
                    'technology': c_data['technology'],
                    'instructor': instructor,
                    'level': c_data['level'],
                    'estimated_minutes': c_data['estimated_minutes'],
                    'is_published': True
                }
            )
            self.stdout.write(self.style.SUCCESS(f"Curso pronto: {course.title}"))

            for idx, l_data in enumerate(c_data['lessons'], start=1):
                lesson, l_created = Lesson.objects.get_or_create(
                    course=course,
                    order=idx,
                    defaults={
                        'title': l_data['title'],
                        'video': l_data['video'],
                        'content': l_data['content'],
                        'duration_seconds': l_data['duration']
                    }
                )
                if l_created:
                    self.stdout.write(f"  - Aula adicionada: {lesson.title}")

        self.stdout.write(self.style.SUCCESS("Catálogo da Onda 2 semeado com sucesso!"))
