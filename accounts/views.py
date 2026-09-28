from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LoginForm, ProfileEditForm
from .models import Profile


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('feed')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(request=request)
            login(request, user)
            messages.success(request, f"Conta criada com sucesso! Seja bem-vindo ao CodeView, {user.first_name}!")
            return redirect('feed')
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')

    next_url = request.GET.get('next', 'feed')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            # Como USERNAME_FIELD = 'email', Django usa o argumento username=email
            user = authenticate(request, username=email, password=password)
            if user is None:
                # Fallback para caso algum backend espere email=
                user = authenticate(request, email=email, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Olá novamente, {user.first_name or user.email}!")
                    return redirect(next_url if next_url else 'feed')
                else:
                    form.add_error(None, "Esta conta está inativa.")
            else:
                form.add_error(None, "E-mail ou senha inválidos.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "Você encerrou sua sessão com segurança.")
    return redirect('login')


def terms_view(request):
    return render(request, 'legal/terms.html')


def privacy_view(request):
    return render(request, 'legal/privacy.html')


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'user': request.user,
    })


@login_required
def profile_edit_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            profile.bio = form.cleaned_data['bio']
            profile.github_url = form.cleaned_data['github_url']
            profile.linkedin_url = form.cleaned_data['linkedin_url']

            if 'avatar' in request.FILES:
                profile.avatar = form.cleaned_data['avatar']

            profile.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('profile')
    else:
        initial_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': profile.bio,
            'github_url': profile.github_url,
            'linkedin_url': profile.linkedin_url,
        }
        form = ProfileEditForm(initial=initial_data)

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'profile': profile,
    })
