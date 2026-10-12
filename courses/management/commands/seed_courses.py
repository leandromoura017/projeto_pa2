from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from videos.models import Technology, Video
from courses.models import Course, Lesson, Challenge

User = get_user_model()


class Command(BaseCommand):
    help = "Popula o banco de dados com mini-cursos, aulas e desafios práticos para a Onda 2."

    def handle(self, *args, **options):
        from accounts.models import Profile, DirectMessage

        # 1. Obter instrutor padrão (admin) e configurar como Mentor
        instructor = User.objects.filter(is_superuser=True).first()
        if not instructor:
            instructor = User.objects.create_superuser('admin@codeview.com', 'admin12345', first_name='Prof. Lucas (Mentor)')
        elif not instructor.first_name:
            instructor.first_name = 'Prof. Lucas (Mentor)'
            instructor.save()

        inst_profile, _ = Profile.objects.get_or_create(user=instructor)
        inst_profile.is_mentor = True
        inst_profile.specialties = 'Python, Django, Arquitetura Backend'
        if not inst_profile.bio:
            inst_profile.bio = 'Engenheiro de Software Sênior e Mentor no CodeView. Focado em Python, Django e automações práticas.'
        inst_profile.save()

        # Criar segunda mentora para o diretório de Perfis & DMs (Onda 4)
        mentor_ana, created_ana = User.objects.get_or_create(
            email='mentora.ana@codeview.com',
            defaults={
                'username': 'mentora_ana',
                'first_name': 'Ana Clara',
                'last_name': 'Silva',
                'is_active': True,
            }
        )
        if created_ana:
            mentor_ana.set_password('Mentor123!')
            mentor_ana.save()
        ana_profile, _ = Profile.objects.get_or_create(user=mentor_ana)
        ana_profile.is_mentor = True
        ana_profile.specialties = 'JavaScript Assíncrono, APIs REST & Frontend'
        ana_profile.bio = 'Tech Lead e Mentora Fullstack no CodeView. Ajudo devs a destravarem no JavaScript e conquistarem certificações práticas.'
        ana_profile.save()

        # Semear mensagem de boas-vindas de mentoria se houver usuário de teste
        student_user = User.objects.filter(email='test_nav@codeview.com').first()
        if student_user and not DirectMessage.objects.filter(sender=mentor_ana, recipient=student_user).exists():
            DirectMessage.objects.create(
                sender=mentor_ana,
                recipient=student_user,
                content='Olá! Sou a mentora Ana Clara. Qualquer dúvida nos desafios práticos ou nos mini-cursos, pode me chamar aqui na DM!'
            )

        # 2. Obter Tecnologias
        tech_python = Technology.objects.filter(slug='python').first()
        tech_js = Technology.objects.filter(slug='javascript').first()
        tech_django = Technology.objects.filter(slug='django').first()

        video_python = Video.objects.filter(technology=tech_python).first()
        video_js = Video.objects.filter(technology=tech_js).first()
        video_django = Video.objects.filter(technology=tech_django).first()

        # 3. Criar Cursos com Desafios
        courses_data = [
            {
                'title': 'Automação de Processos com Python',
                'slug': 'automacao-processos-python',
                'description': 'Aprenda a eliminar tarefas repetitivas e criar scripts rápidos de automação para o seu dia a dia e para a sua empresa.',
                'technology': tech_python,
                'level': 'iniciante',
                'estimated_minutes': 25,
                'lessons': [
                    {
                        'title': 'Loops e List Comprehensions Eficientes',
                        'video': video_python,
                        'content': 'Transformando loops longos em sintaxe elegante de uma linha.',
                        'duration': 45,
                        'challenge': {
                            'title': 'Filtrando números pares com List Comprehension',
                            'question_text': 'Complete a expressão Python para filtrar apenas os números pares da lista numeros = [1, 2, 3, 4, 5, 6]:',
                            'code_snippet': 'numeros = [1, 2, 3, 4, 5, 6]\n# Qual expressão retorna apenas [2, 4, 6] de forma idiomática?',
                            'option_a': '[x for x in numeros if x % 2 == 0]',
                            'option_b': '[x if x % 2 == 0 for x in numeros]',
                            'option_c': 'numeros.filter(x => x % 2 == 0)',
                            'option_d': '[x for x in numeros where x % 2 == 0]',
                            'correct_option': 'A',
                            'explanation': 'Exato! Em Python, a cláusula "if" em uma list comprehension simples sempre vai ao final da expressão.',
                            'points': 15,
                        }
                    },
                    {
                        'title': 'Macetes de Dicionários e Tratamento de Erros',
                        'video': None,
                        'content': 'Como usar .get() para evitar crashes em rotinas de dados.',
                        'duration': 60,
                        'challenge': {
                            'title': 'Evitando KeyError com .get()',
                            'question_text': 'Qual é a forma segura de acessar a chave "telefone" em um dicionário dados sem gerar exceção KeyError se ela não existir?',
                            'code_snippet': 'dados = {"nome": "Carlinhos", "email": "carlinhos@dev.com"}',
                            'option_a': 'telefone = dados.get("telefone", "Não informado")',
                            'option_b': 'telefone = dados["telefone"] or None',
                            'option_c': 'telefone = dados.fetch("telefone")',
                            'option_d': 'telefone = dados.find("telefone")',
                            'correct_option': 'A',
                            'explanation': 'Correto! O método .get(chave, default) retorna o valor padrão seguro caso a chave não exista no dicionário.',
                            'points': 10,
                        }
                    },
                    {
                        'title': 'Automatizando Leitura de Arquivos e Relatórios',
                        'video': None,
                        'content': 'Script prático para consolidar dados automaticamente.',
                        'duration': 90,
                    },
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
                    {
                        'title': 'Async / Await e Promessas sem Callback Hell',
                        'video': video_js,
                        'content': 'Entenda como o event loop do V8 processa chamadas assíncronas.',
                        'duration': 50,
                        'challenge': {
                            'title': 'Capturando erros com Async / Await',
                            'question_text': 'Ao utilizar async/await no JavaScript, qual estrutura de controle é o padrão idiomático para capturar exceções e rejeições de Promises?',
                            'code_snippet': 'async function buscarDados() {\n    // Como proteger a chamada assíncrona?\n    const res = await api.get();\n}',
                            'option_a': 'Bloco try...catch',
                            'option_b': 'Cláusula if (error)',
                            'option_c': 'Callback onError()',
                            'option_d': 'Operador ?? de coalescência',
                            'correct_option': 'A',
                            'explanation': 'Perfeito! Em funções assíncronas, o bloco try...catch é a forma recomendada e limpa para captura de erros.',
                            'points': 15,
                        }
                    },
                    {
                        'title': 'Consumindo APIs REST com Fetch Moderno',
                        'video': None,
                        'content': 'Tratamento de status HTTP, headers e respostas JSON.',
                        'duration': 75,
                    },
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
                    {
                        'title': 'Custom User Model sem dor de cabeça',
                        'video': video_django,
                        'content': 'Por que e como herdar de AbstractUser antes da primeira migração.',
                        'duration': 60,
                        'challenge': {
                            'title': 'Configuração do AUTH_USER_MODEL',
                            'question_text': 'Por que a documentação oficial do Django recomenda configurar um modelo customizado de usuário antes de rodar a primeira migração no projeto?',
                            'code_snippet': '# settings.py\nAUTH_USER_MODEL = "accounts.User"',
                            'option_a': 'Porque alterar o modelo de usuário após a criação de tabelas existentes gera conflitos complexos no banco.',
                            'option_b': 'Porque o Django proíbe autenticação de sessão no modelo padrão.',
                            'option_c': 'Para que o Django desative senhas com hash.',
                            'option_d': 'Porque o Django Admin não aceita o User padrão.',
                            'correct_option': 'A',
                            'explanation': 'Correto! Mudar o modelo de usuário após criar chaves estrangeiras no banco de dados exige migrações manuais delicadas.',
                            'points': 20,
                        }
                    },
                    {
                        'title': 'Otimização de Queries com select_related',
                        'video': None,
                        'content': 'Eliminando o problema clássico de N+1 queries no Django.',
                        'duration': 80,
                    },
                ]
            }
        ]

        for c_data in courses_data:
            course, _ = Course.objects.get_or_create(
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
                lesson, _ = Lesson.objects.get_or_create(
                    course=course,
                    order=idx,
                    defaults={
                        'title': l_data['title'],
                        'video': l_data.get('video'),
                        'content': l_data['content'],
                        'duration_seconds': l_data['duration']
                    }
                )
                self.stdout.write(f"  - Aula pronta: {lesson.title}")

                # Criar desafio se especificado
                c_info = l_data.get('challenge')
                if c_info:
                    challenge, c_created = Challenge.objects.get_or_create(
                        lesson=lesson,
                        defaults={
                            'title': c_info['title'],
                            'question_text': c_info['question_text'],
                            'code_snippet': c_info.get('code_snippet', ''),
                            'option_a': c_info['option_a'],
                            'option_b': c_info['option_b'],
                            'option_c': c_info['option_c'],
                            'option_d': c_info.get('option_d', ''),
                            'correct_option': c_info['correct_option'],
                            'explanation': c_info['explanation'],
                            'points': c_info.get('points', 10),
                        }
                    )
                    if c_created:
                        self.stdout.write(self.style.SUCCESS(f"    [DESAFIO] Desafio cadastrado: {challenge.title}"))

        self.stdout.write(self.style.SUCCESS("Catalogo e Desafios da Onda 2 semeados com sucesso!"))
