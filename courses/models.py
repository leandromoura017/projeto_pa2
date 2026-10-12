from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid
from videos.models import Technology, Video


class Course(models.Model):
    """
    Mini-Curso prático estruturado em pílulas de conhecimento.
    """
    LEVEL_CHOICES = [
        ('iniciante', 'Iniciante'),
        ('intermediario', 'Intermediário'),
        ('avancado', 'Avançado'),
    ]

    title = models.CharField(max_length=150, verbose_name="Título do Mini-Curso")
    slug = models.SlugField(max_length=150, unique=True, verbose_name="Slug (Identificador URL)")
    description = models.TextField(verbose_name="Descrição do Curso")
    technology = models.ForeignKey(
        Technology,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name="Tecnologia Principal"
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='instructed_courses',
        verbose_name="Instrutor / Criador"
    )
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='iniciante',
        verbose_name="Nível de Dificuldade"
    )
    estimated_minutes = models.PositiveIntegerField(default=30, verbose_name="Duração Estimada (minutos)")
    thumbnail = models.ImageField(upload_to='courses/', null=True, blank=True, verbose_name="Imagem de Capa")
    is_published = models.BooleanField(default=True, verbose_name="Publicado no Catálogo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Mini-Curso"
        verbose_name_plural = "Mini-Cursos"
        ordering = ['-created_at']

    def __str__(self):
        tech_name = self.technology.name if self.technology else "Geral"
        return f"{self.title} [{tech_name}]"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def total_lessons(self):
        return self.lessons.count()

    def get_user_progress(self, user):
        """
        Retorna (completed_count, total_count, percentage) para um aluno.
        """
        if not user or not user.is_authenticated:
            total = self.total_lessons
            return (0, total, 0)
        total = self.lessons.count()
        if total == 0:
            return (0, 0, 0)
        completed = LessonProgress.objects.filter(
            user=user,
            lesson__course=self,
            is_completed=True
        ).count()
        pct = int(round((completed / total) * 100))
        return (completed, total, min(pct, 100))


class Lesson(models.Model):
    """
    Aula / Pílula integrante de um Mini-Curso.
    Pode opcionalmente conectar-se a um Video vertical existente no feed.
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Mini-Curso"
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lessons',
        verbose_name="Pílula de Vídeo Associada"
    )
    title = models.CharField(max_length=150, verbose_name="Título da Aula")
    order = models.PositiveIntegerField(default=1, verbose_name="Ordem na Trilha")
    content = models.TextField(blank=True, verbose_name="Conteúdo Complementar / Código")
    duration_seconds = models.PositiveIntegerField(default=60, verbose_name="Duração da Aula (segundos)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")

    class Meta:
        verbose_name = "Aula da Trilha"
        verbose_name_plural = "Aulas da Trilha"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.course.title} - Aula {self.order}: {self.title}"


class Enrollment(models.Model):
    """
    Inscrição / Matrícula do aluno em um Mini-Curso.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Aluno"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Mini-Curso"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name="Data da Matrícula")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Data de Conclusão")
    is_active = models.BooleanField(default=True, verbose_name="Matrícula Ativa")

    class Meta:
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        unique_together = ('user', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        status = "Concluído" if self.completed_at else "Em Andamento"
        return f"{self.user.email} -> {self.course.title} ({status})"

    @property
    def is_completed(self):
        return self.completed_at is not None


class LessonProgress(models.Model):
    """
    Rastreamento de conclusão individual de cada aula da trilha pelo aluno (Onda 4).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        verbose_name="Aluno"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name="Aula"
    )
    is_completed = models.BooleanField(default=True, verbose_name="Concluída")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Concluída em")

    class Meta:
        verbose_name = "Progresso de Aula"
        verbose_name_plural = "Progressos de Aulas"
        unique_together = ('user', 'lesson')
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.email} concluiu {self.lesson.title}"


class Challenge(models.Model):
    """
    Desafio prático / pergunta interativa vinculada a uma aula.
    Fornece verificação com feedback instantâneo (múltipla escolha e/ou submissão de código).
    """
    OPTION_CHOICES = [
        ('A', 'Opção A'),
        ('B', 'Opção B'),
        ('C', 'Opção C'),
        ('D', 'Opção D'),
    ]

    lesson = models.OneToOneField(
        Lesson,
        on_delete=models.CASCADE,
        related_name='challenge',
        verbose_name="Aula Associada"
    )
    title = models.CharField(max_length=150, verbose_name="Título do Desafio")
    question_text = models.TextField(verbose_name="Enunciado da Questão")
    code_snippet = models.TextField(blank=True, verbose_name="Código de Exemplo / Contexto")
    option_a = models.CharField(max_length=255, verbose_name="Opção A")
    option_b = models.CharField(max_length=255, verbose_name="Opção B")
    option_c = models.CharField(max_length=255, verbose_name="Opção C")
    option_d = models.CharField(max_length=255, blank=True, verbose_name="Opção D")
    correct_option = models.CharField(
        max_length=1,
        choices=OPTION_CHOICES,
        verbose_name="Opção Correta"
    )
    expected_code_keyword = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Token/Palavra-chave Esperada no Código (Opcional)"
    )
    explanation = models.TextField(verbose_name="Explicação / Feedback da Resposta")
    points = models.PositiveIntegerField(default=10, verbose_name="Pontos de Domínio")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Desafio Prático"
        verbose_name_plural = "Desafios Práticos"

    def __str__(self):
        return f"Desafio: {self.title} ({self.lesson.course.title})"


class ChallengeAttempt(models.Model):
    """
    Registro da tentativa de resposta ou submissão de código do aluno no desafio prático.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='challenge_attempts',
        verbose_name="Aluno"
    )
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name="Desafio"
    )
    selected_option = models.CharField(max_length=1, blank=True, default='', verbose_name="Opção Selecionada")
    submitted_code = models.TextField(blank=True, default='', verbose_name="Código Submetido")
    is_correct = models.BooleanField(default=False, verbose_name="Acertou?")
    attempted_at = models.DateTimeField(auto_now=True, verbose_name="Última Tentativa")

    class Meta:
        verbose_name = "Tentativa de Desafio"
        verbose_name_plural = "Tentativas de Desafios"
        unique_together = ('user', 'challenge')
        ordering = ['-attempted_at']

    def __str__(self):
        result = "Acerto" if self.is_correct else "Erro"
        return f"{self.user.email} - {self.challenge.title} [{result}]"


class Certificate(models.Model):
    """
    Certificado Digital verificável emitido ao concluir 100% de um Mini-Curso (Onda 4).
    Integra automaticamente o Portfólio Vivo do aluno.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name="Aluno Certificado"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name="Mini-Curso Concluído"
    )
    validation_code = models.CharField(
        max_length=32,
        unique=True,
        verbose_name="Código de Autenticidade"
    )
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Emissão")

    class Meta:
        verbose_name = "Certificado Digital"
        verbose_name_plural = "Certificados Digitais"
        unique_together = ('user', 'course')
        ordering = ['-issued_at']

    def __str__(self):
        return f"Certificado {self.validation_code} - {self.user.email} ({self.course.title})"

    def save(self, *args, **kwargs):
        if not self.validation_code:
            self.validation_code = f"CV-2026-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


