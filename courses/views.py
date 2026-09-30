from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from videos.models import Technology
from .models import Course, Enrollment


def course_list_view(request):
    """
    Catálogo de Mini-Cursos práticos com suporte a filtros
    por tecnologia, nível de dificuldade e busca textual.
    """
    tech_slug = request.GET.get('tech', '').strip()
    level = request.GET.get('level', '').strip()
    query = request.GET.get('q', '').strip()

    courses = Course.objects.filter(is_published=True).select_related('technology', 'instructor').prefetch_related('lessons')
    technologies = Technology.objects.filter(is_active=True).order_by('name')

    if tech_slug:
        courses = courses.filter(technology__slug=tech_slug)

    if level:
        courses = courses.filter(level=level)

    if query:
        courses = courses.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Identificar IDs dos cursos em que o usuário logado já está matriculado
    enrolled_course_ids = set()
    if request.user.is_authenticated:
        enrolled_course_ids = set(
            Enrollment.objects.filter(user=request.user, is_active=True).values_list('course_id', flat=True)
        )

    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'technologies': technologies,
        'current_tech': tech_slug,
        'current_level': level,
        'query': query,
        'enrolled_course_ids': enrolled_course_ids,
    })


def course_detail_view(request, slug):
    """
    Página de detalhes do Mini-Curso: ementa de pílulas/aulas,
    informações do instrutor e botão de matrícula.
    """
    course = get_object_or_404(
        Course.objects.select_related('technology', 'instructor').prefetch_related('lessons__video'),
        slug=slug,
        is_published=True
    )
    
    is_enrolled = False
    enrollment = None
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, course=course, is_active=True).first()
        is_enrolled = enrollment is not None

    lessons = course.lessons.all().order_by('order', 'id')

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
    })


@login_required
def enroll_course_view(request, slug):
    """
    Ação de matrícula do aluno no curso.
    """
    if request.method != 'POST':
        return redirect('course_detail', slug=slug)

    course = get_object_or_404(Course, slug=slug, is_published=True)

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'is_active': True}
    )

    if not created and not enrollment.is_active:
        enrollment.is_active = True
        enrollment.save()
        messages.success(request, f"Matrícula reativada com sucesso no curso '{course.title}'!")
    elif created:
        messages.success(request, f"Parabéns! Você se matriculou no curso '{course.title}'!")
    else:
        messages.info(request, f"Você já está matriculado no curso '{course.title}'.")

    return redirect('course_detail', slug=slug)


from django.http import JsonResponse
import json
from .models import Course, Lesson, Enrollment, Challenge, ChallengeAttempt


@login_required
def unenroll_course_view(request, slug):
    """
    Ação de cancelamento de matrícula no curso.
    """
    if request.method != 'POST':
        return redirect('course_detail', slug=slug)

    course = get_object_or_404(Course, slug=slug)
    enrollment = Enrollment.objects.filter(user=request.user, course=course, is_active=True).first()

    if enrollment:
        enrollment.is_active = False
        enrollment.save()
        messages.warning(request, f"Você cancelou sua matrícula no curso '{course.title}'.")

    return redirect('course_detail', slug=slug)


@login_required
def lesson_challenge_view(request, lesson_id):
    """
    Tela de Desafio Prático / Pergunta de fixação atrelada à aula,
    com suporte a resposta via formulário clássico ou requisição AJAX/Fetch
    para feedback instantâneo na tela.
    """
    lesson = get_object_or_404(
        Lesson.objects.select_related('course', 'video'),
        id=lesson_id
    )

    try:
        challenge = lesson.challenge
    except Challenge.DoesNotExist:
        messages.info(request, "Esta aula ainda não possui um desafio prático cadastrado.")
        return redirect('course_detail', slug=lesson.course.slug)

    # Identificar tentativa anterior do aluno
    attempt = ChallengeAttempt.objects.filter(user=request.user, challenge=challenge).first()

    # Identificar próxima aula da trilha
    next_lesson = Lesson.objects.filter(
        course=lesson.course,
        order__gt=lesson.order
    ).order_by('order').first()

    if request.method == 'POST':
        selected_option = request.POST.get('selected_option', '').strip().upper()
        if not selected_option and request.content_type == 'application/json':
            try:
                body_data = json.loads(request.body)
                selected_option = body_data.get('selected_option', '').strip().upper()
            except Exception:
                selected_option = ''

        if selected_option not in ['A', 'B', 'C', 'D']:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({'status': 'error', 'message': 'Opção inválida selecionada.'}, status=400)
            messages.error(request, "Por favor, selecione uma opção válida.")
            return redirect('lesson_challenge', lesson_id=lesson.id)

        is_correct = (selected_option == challenge.correct_option)

        if attempt:
            attempt.selected_option = selected_option
            attempt.is_correct = is_correct
            attempt.save()
        else:
            attempt = ChallengeAttempt.objects.create(
                user=request.user,
                challenge=challenge,
                selected_option=selected_option,
                is_correct=is_correct
            )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            next_url = ""
            if next_lesson:
                next_url = f"/courses/aulas/{next_lesson.id}/desafio/"
            else:
                next_url = f"/courses/{lesson.course.slug}/"

            return JsonResponse({
                'status': 'success',
                'is_correct': is_correct,
                'selected_option': selected_option,
                'correct_option': challenge.correct_option,
                'explanation': challenge.explanation,
                'points': challenge.points if is_correct else 0,
                'next_lesson_url': next_url,
            })

    return render(request, 'courses/challenge.html', {
        'lesson': lesson,
        'course': lesson.course,
        'challenge': challenge,
        'attempt': attempt,
        'next_lesson': next_lesson,
    })

