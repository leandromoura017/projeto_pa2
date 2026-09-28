from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUserManager(BaseUserManager):
    """
    Gerenciador customizado onde o e-mail é o identificador único
    para autenticação no lugar de username.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório para o cadastro.')
        email = self.normalize_email(email)
        
        # Garante que um username seja preenchido se não fornecido
        if 'username' not in extra_fields or not extra_fields['username']:
            extra_fields['username'] = email.split('@')[0]

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário deve conter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário deve conter is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Modelo de usuário customizado do CodeView.
    Utiliza e-mail único como chave de login principal.
    """
    email = models.EmailField(unique=True, verbose_name="E-mail")

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name']

    def __str__(self):
        return self.email


class Profile(models.Model):
    """
    Perfil do dev/aluno no CodeView (Portfólio Vivo).
    Sem upload de currículo em anexo: a atuação na plataforma é a validação técnica.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Foto de Perfil")
    bio = models.CharField(max_length=250, blank=True, verbose_name="Biografia")
    github_url = models.URLField(blank=True, verbose_name="Link do GitHub")
    linkedin_url = models.URLField(blank=True, verbose_name="Link do LinkedIn")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return f"Perfil de {self.user.email}"


class UserConsent(models.Model):
    """
    Registro formal e auditável de consentimento aos Termos de Uso e LGPD.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consents')
    terms_version = models.CharField(max_length=20, default='v1.0-2026', verbose_name="Versão dos Termos")
    accepted_at = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora do Consentimento")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Endereço IP")

    def __str__(self):
        return f"Consentimento LGPD ({self.terms_version}) - {self.user.email}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
