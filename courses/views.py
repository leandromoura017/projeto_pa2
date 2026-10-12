from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
import json
from videos.models import Technology
from .models import (
    Course,
    Lesson,
    Enrollment,
    LessonProgress,
    Challenge,
    ChallengeAttempt,
    Certificate,
)


def _sync_course_completion(user, course):
    """
    Atualiza o status de conclusão da matrícula caso o aluno tenha atingido 100% das aulas.
    """
    completed_count, total_count, pct = course.get_user_progress(user)
    if total_count > 0 and completed_count >= total_count:
        enrollment, _ = Enrollment.objects.get_or_create(
            user=user,
            course=course,
            defaults={'is_active': True, 'completed_at': timezone.now()}
        )
        if not enrollment.completed_at:
            enrollment.completed_at = timezone.now()
            enrollment.is_active = True
            enrollment.save()
    return completed_count, total_count, pct


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
    progresso percentual, informações do instrutor, matrícula e emissão de certificado.
    """
    course = get_object_or_404(
        Course.objects.select_related('technology', 'instructor').prefetch_related('lessons__video'),
        slug=slug,
        is_published=True
    )
    
    is_enrolled = False
    enrollment = None
    completed_lesson_ids = set()
    completed_count, total_count, progress_pct = (0, course.lessons.count(), 0)
    certificate = None

    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, course=course, is_active=True).first()
        is_enrolled = enrollment is not None
        completed_lesson_ids = set(
            LessonProgress.objects.filter(
                user=request.user,
                lesson__course=course,
                is_completed=True
            ).values_list('lesson_id', flat=True)
        )
        completed_count, total_count, progress_pct = _sync_course_completion(request.user, course)
        if completed_count > 0 and not is_enrolled:
            enrollment = Enrollment.objects.filter(user=request.user, course=course, is_active=True).first()
            is_enrolled = enrollment is not None
        certificate = Certificate.objects.filter(user=request.user, course=course).first()

    lessons = course.lessons.all().order_by('order', 'id')

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'completed_lesson_ids': completed_lesson_ids,
        'completed_count': completed_count,
        'total_count': total_count,
        'progress_pct': progress_pct,
        'certificate': certificate,
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
def complete_lesson_view(request, lesson_id):
    """
    Marca uma aula/pílula como concluída pelo aluno e atualiza o progresso da trilha (Onda 4).
    """
    if request.method != 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)
        return redirect('course_detail', slug=lesson.course.slug)

    lesson = get_object_or_404(Lesson.objects.select_related('course'), id=lesson_id)
    course = lesson.course

    Enrollment.objects.update_or_create(
        user=request.user,
        course=course,
        defaults={'is_active': True}
    )

    LessonProgress.objects.update_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'is_completed': True}
    )

    completed_count, total_count, progress_pct = _sync_course_completion(request.user, course)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'status': 'success',
            'lesson_id': lesson.id,
            'completed_count': completed_count,
            'total_count': total_count,
            'progress_pct': progress_pct,
        })

    messages.success(request, f"Aula '{lesson.title}' marcada como concluída! Progresso: {progress_pct}%.")
    return redirect('course_detail', slug=course.slug)


@login_required
def lesson_challenge_view(request, lesson_id):
    """
    Tela de Desafio Prático / Pergunta de fixação atrelada à aula,
    com suporte a resposta de múltipla escolha E submissão de código prático (Onda 3),
    além de atualização automática de progresso da aula (Onda 4).
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

    attempt = ChallengeAttempt.objects.filter(user=request.user, challenge=challenge).first()

    next_lesson = Lesson.objects.filter(
        course=lesson.course,
        order__gt=lesson.order
    ).order_by('order').first()

    if request.method == 'POST':
        selected_option = request.POST.get('selected_option', '').strip().upper()
        submitted_code = request.POST.get('submitted_code', '').strip()

        if request.content_type == 'application/json':
            try:
                body_data = json.loads(request.body)
                selected_option = body_data.get('selected_option', selected_option).strip().upper()
                submitted_code = body_data.get('submitted_code', submitted_code).strip()
            except Exception:
                pass

        has_valid_option = selected_option in ['A', 'B', 'C', 'D']
        has_code = len(submitted_code) > 0

        if not has_valid_option and not has_code:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Selecione uma alternativa ou envie seu código prático.'
                }, status=400)
            messages.error(request, "Por favor, selecione uma opção válida ou envie seu código prático.")
            return redirect('lesson_challenge', lesson_id=lesson.id)

        # Validação da resposta (opção e/ou submissão de código)
        if has_valid_option:
            is_correct = (selected_option == challenge.correct_option)
        else:
            # Validação por submissão de código prático
            if challenge.expected_code_keyword:
                is_correct = challenge.expected_code_keyword.lower() in submitted_code.lower()
            else:
                is_correct = len(submitted_code) >= 3

        if attempt:
            if has_valid_option:
                attempt.selected_option = selected_option
            if has_code:
                attempt.submitted_code = submitted_code
            attempt.is_correct = is_correct
            attempt.save()
        else:
            attempt = ChallengeAttempt.objects.create(
                user=request.user,
                challenge=challenge,
                selected_option=selected_option if has_valid_option else '',
                submitted_code=submitted_code,
                is_correct=is_correct
            )

        # Se acertou o desafio, marca automaticamente a aula como concluída no Progresso do Curso (Onda 4)
        if is_correct:
            Enrollment.objects.update_or_create(
                user=request.user,
                course=lesson.course,
                defaults={'is_active': True}
            )
            LessonProgress.objects.update_or_create(
                user=request.user,
                lesson=lesson,
                defaults={'is_completed': True}
            )
            _sync_course_completion(request.user, lesson.course)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
            next_url = f"/courses/aulas/{next_lesson.id}/desafio/" if next_lesson else f"/courses/{lesson.course.slug}/"
            return JsonResponse({
                'status': 'success',
                'is_correct': is_correct,
                'selected_option': attempt.selected_option,
                'submitted_code': attempt.submitted_code,
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


@login_required
def issue_certificate_view(request, slug):
    """
    Emite o Certificado Digital verificável para o aluno que concluiu 100% do Mini-Curso (Onda 4).
    """
    if request.method != 'POST':
        return redirect('course_detail', slug=slug)

    course = get_object_or_404(Course, slug=slug, is_published=True)
    completed_count, total_count, progress_pct = _sync_course_completion(request.user, course)

    if total_count == 0 or completed_count < total_count:
        messages.warning(
            request,
            f"Você concluiu {completed_count} de {total_count} aulas ({progress_pct}%). Conclua 100% da trilha para emitir seu Certificado Digital!"
        )
        return redirect('course_detail', slug=slug)

    certificate, created = Certificate.objects.get_or_create(
        user=request.user,
        course=course
    )

    if created:
        messages.success(request, f"Parabéns! Seu Certificado Digital do curso '{course.title}' foi emitido com sucesso!")
    else:
        messages.info(request, f"Exibindo seu Certificado Digital emitido para '{course.title}'.")

    return redirect('certificate_detail', validation_code=certificate.validation_code)


def certificate_detail_view(request, validation_code):
    """
    Página pública de visualização e validação de autenticidade do Certificado Digital (Onda 4).
    """
    certificate = get_object_or_404(
        Certificate.objects.select_related('user', 'course', 'course__technology', 'course__instructor'),
        validation_code=validation_code
    )
    return render(request, 'courses/certificate_detail.html', {
        'certificate': certificate,
        'course': certificate.course,
        'student': certificate.user,
    })

