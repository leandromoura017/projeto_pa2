from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import SignUpForm, LoginForm


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


def feed_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'feed.html')
