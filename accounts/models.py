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
    specialties = models.CharField(max_length=150, blank=True, verbose_name="Especialidades Técnicas")
    is_mentor = models.BooleanField(default=False, verbose_name="É Mentor / Instrutor")
    github_url = models.URLField(blank=True, verbose_name="Link do GitHub")
    linkedin_url = models.URLField(blank=True, verbose_name="Link do LinkedIn")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return f"Perfil de {self.user.email}"


class DirectMessage(models.Model):
    """
    Mensagem direta (DM) entre alunos e mentores/instrutores na plataforma.
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name="Remetente"
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name="Destinatário"
    )
    content = models.TextField(max_length=1000, verbose_name="Mensagem")
    is_read = models.BooleanField(default=False, verbose_name="Lida")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Enviada em")

    class Meta:
        verbose_name = "Mensagem Direta (DM)"
        verbose_name_plural = "Mensagens Diretas (DMs)"
        ordering = ['created_at']

    def __str__(self):
        return f"DM de {self.sender.email} para {self.recipient.email}"


class Notification(models.Model):
    """
    Notificação / Alerta (sininho) para o usuário sobre novas publicações,
    conquistas e mensagens (Onda 5 - #23).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Usuário Notificado"
    )
    title = models.CharField(max_length=150, verbose_name="Título do Alerta")
    message = models.TextField(verbose_name="Mensagem")
    link = models.CharField(max_length=255, blank=True, verbose_name="Link de Destino")
    icon = models.CharField(max_length=20, default='🔔', verbose_name="Ícone")
    is_read = models.BooleanField(default=False, verbose_name="Lida")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "Notificações"
        ordering = ['-created_at']

    def __str__(self):
        return f"Alerta ({self.icon}) para {self.user.email}: {self.title}"


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


class TAMEvaluation(models.Model):
    """
    Coleta estruturada de dados empíricos de aceitação da tecnologia
    baseado no Technology Acceptance Model (Davis, 1989) para o PA2.
    """
    ROLE_CHOICES = [
        ('estudante', 'Estudante de TI / Computação'),
        ('dev_junior', 'Desenvolvedor(a) Júnior / Estagiário(a)'),
        ('dev_pleno_senior', 'Desenvolvedor(a) Pleno / Sênior / Lead'),
        ('recruiter', 'Recrutador(a) / Tech Recruiter / RH'),
        ('professor', 'Professor(a) / Instrutor(a) / Mentor(a)'),
        ('outro', 'Outro perfil profissional'),
    ]

    EXPERIENCE_CHOICES = [
        ('menos_1_ano', 'Menos de 1 ano (Iniciante)'),
        ('1_a_3_anos', 'De 1 a 3 anos'),
        ('3_a_5_anos', 'De 3 a 5 anos'),
        ('mais_5_anos', 'Mais de 5 anos'),
    ]

    DEVICE_CHOICES = [
        ('desktop', 'Computador Desktop / Notebook'),
        ('mobile', 'Smartphone / Celular'),
        ('tablet', 'Tablet'),
    ]

    LIKERT_CHOICES = [
        (1, '1 - Discordo Totalmente'),
        (2, '2 - Discordo Parcialmente'),
        (3, '3 - Neutro / Indiferente'),
        (4, '4 - Concordo Parcialmente'),
        (5, '5 - Concordo Totalmente'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tam_evaluations',
        verbose_name="Usuário (se logado)"
    )
    evaluator_name = models.CharField(max_length=120, blank=True, verbose_name="Nome (ou Iniciais)")
    evaluator_email = models.EmailField(blank=True, verbose_name="E-mail de Contato")
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, verbose_name="Perfil de Atuação")
    experience = models.CharField(max_length=50, choices=EXPERIENCE_CHOICES, verbose_name="Tempo de Experiência")
    device = models.CharField(max_length=50, choices=DEVICE_CHOICES, verbose_name="Dispositivo Utilizado")

    # Construto PU: Utilidade Percebida (Perceived Usefulness)
    pu1 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="PU1: Pílulas curtas agilizam aprendizado")
    pu2 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="PU2: Desafios instantâneos aumentam fixação")
    pu3 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="PU3: Portfólio Vivo demonstra melhor competências")
    pu4 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="PU4: Cronograma e Certificado com QR agregam valor")
    pu5 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="PU5: CodeView é uma ferramenta útil e vantajosa")

    # Construto PEOU: Facilidade de Uso Percebida (Perceived Ease of Use)
    peou1 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="PEOU1: Navegação clara e intuitiva")
    peou2 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="PEOU2: Interface visual limpa e agradável")
    peou3 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="PEOU3: Submissão de desafios simples")
    peou4 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="PEOU4: Progresso e certificado sem burocracia")
    peou5 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="PEOU5: Fácil de operar sem treinamento")

    # Construto ATU: Atitude em Relação ao Uso (Attitude Toward Using)
    atu1 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="ATU1: Experiência agradável e estimulante")
    atu2 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="ATU2: Formato moderno e engajador")
    atu3 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="ATU3: Percepção geral muito positiva")

    # Construto BIU: Intenção Comportamental de Uso (Behavioral Intention to Use)
    biu1 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="BIU1: Usaria regularmente para atualizar-me")
    biu2 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="BIU2: Indicaria a amigos e colegas de TI")
    biu3 = models.PositiveSmallIntegerField(choices=LIKERT_CHOICES, verbose_name="BIU3: Preferiria ao invés de cursos longos")

    # Avaliação Qualitativa Aberta
    highlights = models.TextField(blank=True, verbose_name="Pontos Fortes / Destaques")
    difficulties = models.TextField(blank=True, verbose_name="Dificuldades ou Atritos")
    suggestions = models.TextField(blank=True, verbose_name="Sugestões de Melhoria")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Submissão")

    class Meta:
        verbose_name = "Avaliação TAM"
        verbose_name_plural = "Avaliações TAM (Pesquisa PA2)"
        ordering = ['-created_at']

    @property
    def display_name(self):
        """
        Retorna o nome do avaliador para exibição segura em templates e relatórios,
        evitando falhas de lookup quando a avaliação for anônima (user=None).
        """
        if self.evaluator_name:
            return self.evaluator_name
        if self.user and getattr(self.user, 'email', None):
            return self.user.email
        if self.evaluator_email:
            return self.evaluator_email
        return "Avaliador Anônimo"

    def __str__(self):
        return f"TAM #{self.id} - {self.display_name} ({self.get_role_display()}) - Média Geral: {self.overall_score:.2f}"

    @property
    def pu_score(self):
        return (self.pu1 + self.pu2 + self.pu3 + self.pu4 + self.pu5) / 5.0

    @property
    def peou_score(self):
        return (self.peou1 + self.peou2 + self.peou3 + self.peou4 + self.peou5) / 5.0

    @property
    def atu_score(self):
        return (self.atu1 + self.atu2 + self.atu3) / 3.0

    @property
    def biu_score(self):
        return (self.biu1 + self.biu2 + self.biu3) / 3.0

    @property
    def overall_score(self):
        return (self.pu_score + self.peou_score + self.atu_score + self.biu_score) / 4.0



@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
