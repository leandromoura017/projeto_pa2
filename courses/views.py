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
