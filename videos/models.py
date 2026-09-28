from django.db import models
from django.conf import settings
from django.utils.text import slugify


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
    video_file = models.FileField(upload_to='videos/', verbose_name="Arquivo de Vídeo (9:16 MP4/WebM)")
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
