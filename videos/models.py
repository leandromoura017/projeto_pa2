import os
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.exceptions import ValidationError

ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov', '.avi', '.mkv', '.m4v'}
BLOCKED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.tiff', '.ico', '.jfif', '.avif'}


def validate_video_file(file):
    """
    Valida se o arquivo enviado é de fato um vídeo e bloqueia uploads de imagens.
    """
    name = getattr(file, 'name', '')
    ext = os.path.splitext(name)[1].lower() if name else ''

    if ext in BLOCKED_IMAGE_EXTENSIONS:
        raise ValidationError("O arquivo selecionado é uma imagem. Por favor, envie um arquivo de vídeo (.mp4, .webm, .mov).")

    if ext and ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(f"Formato de arquivo '{ext}' não suportado. Envie apenas vídeos (.mp4, .webm, .mov, .avi, .mkv).")

    content_type = getattr(file, 'content_type', '')
    if content_type:
        if content_type.startswith('image/'):
            raise ValidationError("O arquivo selecionado é uma imagem. Apenas vídeos são permitidos.")
        if not content_type.startswith('video/') and content_type not in ('application/octet-stream', ''):
            raise ValidationError("O arquivo enviado não é um vídeo válido.")



class Technology(models.Model):
    """
    Categoria / Linguagem de programação (ex: Python, JavaScript, Django, SQL)
    """
    name = models.CharField(max_length=50, unique=True, verbose_name="Nome da Tecnologia")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Slug (Identificador)")
    icon_name = models.CharField(max_length=50, blank=True, verbose_name="Ícone / Sigla")
    is_active = models.BooleanField(default=True, verbose_name="Ativo no Feed")

    class Meta:
        verbose_name = "Tecnologia"
        verbose_name_plural = "Tecnologias"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Video(models.Model):
    """
    Micro-vídeo vertical (formato 9:16) com pílula de conhecimento prático.
    """
    title = models.CharField(max_length=150, verbose_name="Título da Pílula")
    description = models.TextField(blank=True, verbose_name="Descrição / Resumo do Código")
    video_file = models.FileField(
        upload_to='videos/',
        validators=[validate_video_file],
        verbose_name="Arquivo de Vídeo (9:16 MP4/WebM)"
    )
    technology = models.ForeignKey(
        Technology,
        on_delete=models.PROTECT,
        related_name='videos',
        verbose_name="Tecnologia Principal"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='videos',
        verbose_name="Autor / Criador"
    )
    duration_seconds = models.PositiveIntegerField(default=30, verbose_name="Duração em Segundos")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Visualizações")
    is_published = models.BooleanField(default=True, verbose_name="Publicado no Feed")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Cadastrado em")

    class Meta:
        verbose_name = "Micro-Vídeo"
        verbose_name_plural = "Micro-Vídeos"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.technology.name})"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()

    @property
    def trust_count(self):
        """Total de votos de confiança positivos (Onda 7 - #29)."""
        return self.trust_votes.filter(is_trusted=True).count()

    @property
    def has_mentor_trust(self):
        """Verifica se pelo menos um Mentor/Instrutor avaliou positivamente."""
        return self.trust_votes.filter(is_trusted=True, user__profile__is_mentor=True).exists()

    @property
    def is_trusted_content(self):
        """
        Selo 'Conteúdo Confiável' (Onda 7 - #29):
        Atribuído se um Mentor homologou o vídeo OU se acumulou 3+ votos positivos da comunidade.
        """
        return self.has_mentor_trust or (self.trust_count >= 3)


class VideoLike(models.Model):
    """
    Registro de curtida (like) de um usuário em um micro-vídeo do feed.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='video_likes',
        verbose_name="Usuário"
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name="Vídeo"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Curtido em")

    class Meta:
        verbose_name = "Curtida em Vídeo"
        verbose_name_plural = "Curtidas em Vídeos"
        unique_together = ('user', 'video')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} curtiu {self.video.title}"


class VideoComment(models.Model):
    """
    Comentário ou dúvida técnica em um micro-vídeo (Onda 6 - #24).
    """
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Vídeo"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='video_comments',
        verbose_name="Autor do Comentário"
    )
    content = models.TextField(max_length=500, verbose_name="Comentário")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Enviado em")

    class Meta:
        verbose_name = "Comentário de Vídeo"
        verbose_name_plural = "Comentários de Vídeos"
        ordering = ['created_at']

    def __str__(self):
        return f"Comentário de {self.user.email} em {self.video.title}"


class VideoNote(models.Model):
    """
    Bloco de notas pessoal e privado do aluno em cada pílula/vídeo (Onda 7 - #28).
    Apenas o autor da anotação pode visualizar e editar suas notas.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='video_notes',
        verbose_name="Usuário"
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='private_notes',
        verbose_name="Vídeo"
    )
    content = models.TextField(max_length=2000, blank=True, verbose_name="Minhas Anotações Privadas")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizada em")

    class Meta:
        verbose_name = "Anotação Privada de Vídeo"
        verbose_name_plural = "Anotações Privadas de Vídeos"
        unique_together = ('user', 'video')
        ordering = ['-updated_at']

    def __str__(self):
        return f"Anotação de {self.user.email} em {self.video.title}"


class VideoTrustVote(models.Model):
    """
    Voto de confiança da comunidade técnica e mentores (Onda 7 - #29).
    Selo 'Conteúdo Confiável' atribuído a vídeos validados pela comunidade ou mentores.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trust_votes',
        verbose_name="Avaliador"
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='trust_votes',
        verbose_name="Vídeo"
    )
    is_trusted = models.BooleanField(default=True, verbose_name="É Confiável")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Votado em")

    class Meta:
        verbose_name = "Voto de Confiança"
        verbose_name_plural = "Votos de Confiança"
        unique_together = ('user', 'video')
        ordering = ['-created_at']

    def __str__(self):
        status = "Confiável" if self.is_trusted else "Não Confiável"
        return f"{self.user.email} marcou '{self.video.title}' como {status}"
