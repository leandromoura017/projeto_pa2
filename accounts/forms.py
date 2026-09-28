from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .models import User, UserConsent


class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Nome Completo",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Seu nome completo',
            'required': True,
        })
    )
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'seu.email@exemplo.com',
            'required': True,
        })
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Mínimo de 8 caracteres',
            'required': True,
        }),
        help_text="A senha deve ter no mínimo 8 caracteres."
    )
    password_confirm = forms.CharField(
        label="Confirmar Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Repita a senha',
            'required': True,
        })
    )
    lgpd_consent = forms.BooleanField(
        label="Li e concordo com os Termos de Uso e Política de Privacidade (LGPD)",
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500',
        }),
        error_messages={
            'required': 'Você precisa concordar com os Termos de Privacidade para continuar.'
        }
    )

    class Meta:
        model = User
        fields = ('first_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este e-mail já está em uso.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', "As senhas não coincidem.")
            else:
                try:
                    password_validation.validate_password(password, self.instance)
                except ValidationError as error:
                    self.add_error('password', error)

        return cleaned_data

    def save(self, commit=True, request=None):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.username = user.email.split('@')[0]
        
        if commit:
            user.save()
            ip = None
            if request:
                ip = request.META.get('HTTP_X_FORWARDED_FOR')
                if ip:
                    ip = ip.split(',')[0].strip()
                else:
                    ip = request.META.get('REMOTE_ADDR')

            UserConsent.objects.create(
                user=user,
                terms_version='v1.0-2026',
                ip_address=ip
            )
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'seu.email@exemplo.com',
            'required': True,
        })
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Sua senha',
            'required': True,
        })
    )


class ProfileEditForm(forms.Form):
    first_name = forms.CharField(
        label="Primeiro Nome",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent',
            'placeholder': 'Seu primeiro nome',
            'required': True,
        })
    )
    last_name = forms.CharField(
        label="Sobrenome",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent',
            'placeholder': 'Seu sobrenome',
        })
    )
    bio = forms.CharField(
        label="Biografia do Dev",
        max_length=250,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent resize-none',
            'placeholder': 'Ex: Desenvolvedor Python e Django focado em automações e APIs...',
            'rows': 3,
            'maxlength': '250',
            'id': 'bio-textarea'
        }),
        help_text="Máximo de 250 caracteres. Apresente seu foco técnico."
    )
    github_url = forms.URLField(
        label="Link do GitHub",
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent',
            'placeholder': 'https://github.com/seu-usuario',
        })
    )
    linkedin_url = forms.URLField(
        label="Link do LinkedIn",
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'w-full px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent',
            'placeholder': 'https://linkedin.com/in/seu-perfil',
        })
    )
    avatar = forms.ImageField(
        label="Foto de Avatar",
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-xs text-gray-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-cyan-600/20 file:text-cyan-300 hover:file:bg-cyan-600/30 file:cursor-pointer',
            'accept': 'image/jpeg,image/png,image/webp'
        }),
        help_text="Formatos aceitos: JPG, PNG ou WebP. Tamanho máximo: 2MB."
    )

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            max_size = 2 * 1024 * 1024
            if avatar.size > max_size:
                raise ValidationError("O arquivo da foto não pode exceder 2MB.")
        return avatar

