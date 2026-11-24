import io
import json
import qrcode
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

from videos.models import Technology, Video, validate_video_file
from django.core.exceptions import ValidationError
from accounts.models import Notification
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
    Página de detalhes do Mini-Curso: ementa de pílulas/aulas, cronograma de estudos sugerido,
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
    lessons_list = list(lessons)

    # Geração do Cronograma de Estudos Recomendado (Onda 6 - #25)
    schedule_stages = []
    stage_size = max(1, (len(lessons_list) + 2) // 3) if lessons_list else 1
    stage_titles = [
        "Etapa 1: Aquecimento & Fundamentos",
        "Etapa 2: Aplicação Prática & Resolução",
        "Etapa 3: Domínio Técnico & Desafios Finais",
    ]
    stage_days = ["Dia 1 (Sugerido)", "Dia 2 (Sugerido)", "Dia 3 (Sugerido)"]

    for i in range(0, max(len(lessons_list), 1), stage_size):
        chunk = lessons_list[i:i + stage_size]
        if not chunk:
            continue
        idx = i // stage_size
        title = stage_titles[idx] if idx < len(stage_titles) else f"Etapa {idx + 1}: Prática Avançada"
        timing = stage_days[idx] if idx < len(stage_days) else f"Dia {idx + 1}"

        chunk_completed = [l.id in completed_lesson_ids for l in chunk]
        is_all_completed = all(chunk_completed) if chunk_completed else False
        is_in_progress = any(chunk_completed) and not is_all_completed
        status = 'completed' if is_all_completed else ('in_progress' if is_in_progress else 'pending')

        schedule_stages.append({
            'title': title,
            'timing': timing,
            'lessons': chunk,
            'status': status,
            'total_lessons': len(chunk),
            'completed_lessons': sum(chunk_completed),
        })

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'schedule_stages': schedule_stages,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'completed_lesson_ids': completed_lesson_ids,
        'completed_count': completed_count,
        'total_count': total_count,
        'progress_pct': progress_pct,
        'certificate': certificate,
        'is_instructor': request.user.is_authenticated and (request.user == course.instructor or request.user.is_superuser),
    })


@login_required
def enroll_course_view(request, slug):
    """
    Ação de matrícula do aluno no curso.
    Dispara notificação de matrícula confirmada (Onda 6 - #27).
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
        # Notificação de matrícula confirmada (Onda 6 - #27)
        Notification.objects.create(
            user=request.user,
            title="📚 Inscrição Confirmada!",
            message=f"Sua matrícula na trilha '{course.title}' foi confirmada! Explore as pílulas de código e conclua os desafios práticos.",
            link=reverse('course_detail', kwargs={'slug': course.slug}),
            icon='🚀'
        )
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

        # Notificação de matrícula cancelada (Onda 7 - #31)
        Notification.objects.create(
            user=request.user,
            title="⚠️ Matrícula Cancelada",
            message=f"Você cancelou sua matrícula na trilha '{course.title}'. Seu progresso foi pausado.",
            link=reverse('course_detail', kwargs={'slug': course.slug}),
            icon='⚠️'
        )

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
    Tela de Desafios Práticos da aula com suporte a múltiplos desafios por aula,
    questões de múltipla escolha (alternativas) e questões discursivas/código aberto,
    além de acompanhamento inteligente de progresso e fixação imediata.
    """
    lesson = get_object_or_404(
        Lesson.objects.select_related('course', 'video'),
        id=lesson_id
    )

    challenges = list(lesson.challenges.all().order_by('order', 'id'))
    if not challenges:
        messages.info(request, "Esta aula ainda não possui desafios práticos cadastrados.")
        return redirect('course_detail', slug=lesson.course.slug)

    # Seleciona o desafio ativo (via ?c=<id> ou o primeiro pendente)
    selected_c_id = request.GET.get('c')
    challenge = None
    if selected_c_id:
        challenge = next((c for c in challenges if str(c.id) == str(selected_c_id)), None)

    attempts_by_challenge = {
        att.challenge_id: att for att in ChallengeAttempt.objects.filter(user=request.user, challenge__in=challenges)
    }

    if not challenge:
        # Pega o primeiro desafio ainda não resolvido corretamente, ou o primeiro
        for ch in challenges:
            att = attempts_by_challenge.get(ch.id)
            if not att or not att.is_correct:
                challenge = ch
                break
        if not challenge:
            challenge = challenges[0]

    attempt = attempts_by_challenge.get(challenge.id)

    # Próximo desafio dentro da mesma aula (se houver)
    curr_idx = challenges.index(challenge)
    next_challenge_in_lesson = challenges[curr_idx + 1] if curr_idx < len(challenges) - 1 else None

    # Próxima aula na trilha
    next_lesson = Lesson.objects.filter(
        course=lesson.course,
        order__gt=lesson.order
    ).order_by('order').first()

    if request.method == 'POST':
        selected_option = request.POST.get('selected_option', '').strip().upper()
        submitted_code = (request.POST.get('submitted_code') or request.POST.get('answer_text', '')).strip()

        if request.content_type == 'application/json':
            try:
                body_data = json.loads(request.body)
                selected_option = body_data.get('selected_option', selected_option).strip().upper()
                submitted_code = body_data.get('submitted_code', submitted_code).strip()
            except Exception:
                pass

        is_discursive = (challenge.challenge_type == 'discursiva')
        has_valid_option = selected_option in ['A', 'B', 'C', 'D']
        has_text_answer = len(submitted_code) > 0

        if is_discursive:
            if not has_text_answer:
                msg = "Por favor, escreva sua resposta discursiva ou código da solução."
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                    return JsonResponse({'status': 'error', 'message': msg}, status=400)
                messages.error(request, msg)
                return redirect(f"{reverse('lesson_challenge', kwargs={'lesson_id': lesson.id})}?c={challenge.id}")

            # Validação discursiva: confere palavra-chave esperada se configurada, ou extensão mínima
            if challenge.expected_code_keyword:
                is_correct = challenge.expected_code_keyword.lower() in submitted_code.lower()
            else:
                is_correct = len(submitted_code) >= 5
        else:
            # Questão de alternativas
            if not has_valid_option and not has_text_answer:
                msg = "Por favor, selecione uma alternativa válida."
                if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
                    return JsonResponse({'status': 'error', 'message': msg}, status=400)
                messages.error(request, msg)
                return redirect(f"{reverse('lesson_challenge', kwargs={'lesson_id': lesson.id})}?c={challenge.id}")

            if has_valid_option:
                is_correct = (selected_option == challenge.correct_option)
            else:
                if challenge.expected_code_keyword:
                    is_correct = challenge.expected_code_keyword.lower() in submitted_code.lower()
                else:
                    is_correct = len(submitted_code) >= 3

        if attempt:
            if not is_discursive and has_valid_option:
                attempt.selected_option = selected_option
            if has_text_answer:
                attempt.submitted_code = submitted_code
            attempt.is_correct = is_correct
            attempt.save()
        else:
            attempt = ChallengeAttempt.objects.create(
                user=request.user,
                challenge=challenge,
                selected_option=selected_option if not is_discursive else '',
                submitted_code=submitted_code,
                is_correct=is_correct
            )
        attempts_by_challenge[challenge.id] = attempt

        # Verifica se TODOS os desafios da aula estão concluídos com acerto
        all_challenges_completed = True
        for ch in challenges:
            att = attempts_by_challenge.get(ch.id)
            if not att or not att.is_correct:
                all_challenges_completed = False
                break

        # Se todos os desafios da aula foram concluídos com sucesso, marca a aula como concluída
        if all_challenges_completed:
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
            if next_challenge_in_lesson and not attempt.is_correct:
                next_url = f"{reverse('lesson_challenge', kwargs={'lesson_id': lesson.id})}?c={next_challenge_in_lesson.id}"
            elif all_challenges_completed:
                next_url = f"/courses/aulas/{next_lesson.id}/desafio/" if next_lesson else f"/courses/{lesson.course.slug}/"
            elif next_challenge_in_lesson:
                next_url = f"{reverse('lesson_challenge', kwargs={'lesson_id': lesson.id})}?c={next_challenge_in_lesson.id}"
            else:
                next_url = f"/courses/{lesson.course.slug}/"

            return JsonResponse({
                'status': 'success',
                'is_correct': is_correct,
                'is_discursive': is_discursive,
                'selected_option': attempt.selected_option,
                'submitted_code': attempt.submitted_code,
                'correct_option': challenge.correct_option,
                'explanation': challenge.explanation,
                'expected_answer': challenge.expected_answer if is_discursive else '',
                'points': challenge.points if is_correct else 0,
                'all_completed': all_challenges_completed,
                'next_url': next_url,
            })

    # Lista de itens para navegação entre os desafios da aula
    challenge_tabs = []
    for idx, ch in enumerate(challenges, start=1):
        att = attempts_by_challenge.get(ch.id)
        challenge_tabs.append({
            'challenge': ch,
            'index': idx,
            'is_current': (ch.id == challenge.id),
            'is_solved': (att.is_correct if att else False),
        })

    return render(request, 'courses/challenge.html', {
        'lesson': lesson,
        'course': lesson.course,
        'challenge': challenge,
        'challenges': challenges,
        'challenge_tabs': challenge_tabs,
        'current_index': curr_idx + 1,
        'total_challenges': len(challenges),
        'next_challenge_in_lesson': next_challenge_in_lesson,
        'attempt': attempt,
        'next_lesson': next_lesson,
    })


@login_required
def issue_certificate_view(request, slug):
    """
    Emite o Certificado Digital verificável para o aluno que concluiu 100% do Mini-Curso (Onda 4).
    Dispara notificação para o usuário (Onda 5 - #23).
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
        Notification.objects.create(
            user=request.user,
            title="🎓 Certificado Emitido!",
            message=f"Parabéns! Você concluiu a trilha '{course.title}' e seu Certificado Digital já está disponível para validação pública e download.",
            link=reverse('certificate_detail', args=[certificate.validation_code]),
            icon='🎓'
        )
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


def certificate_qr_code_view(request, validation_code):
    """
    Gera dinamicamente a imagem PNG do QR Code que aponta
    para a página pública de validação de autenticidade do certificado (Onda 5 - #21).
    """
    certificate = get_object_or_404(Certificate, validation_code=validation_code)
    public_url = request.build_absolute_uri(
        reverse('certificate_detail', args=[certificate.validation_code])
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2,
    )
    qr.add_data(public_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type='image/png')


def download_certificate_pdf_view(request, validation_code):
    """
    Gera o Certificado de Conclusão em formato PDF de alta fidelidade
    para download oficial pelo aluno (Onda 5 - #20).
    """
    certificate = get_object_or_404(
        Certificate.objects.select_related('user', 'course', 'course__technology', 'course__instructor'),
        validation_code=validation_code
    )
    course = certificate.course
    student = certificate.user
    instructor = course.instructor

    # Gerar QR Code para embutir no PDF
    public_url = request.build_absolute_uri(
        reverse('certificate_detail', args=[certificate.validation_code])
    )
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=1,
    )
    qr.add_data(public_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format='PNG')
    qr_buf.seek(0)

    # Canvas do ReportLab em Landscape A4
    buf = io.BytesIO()
    p = canvas.Canvas(buf, pagesize=landscape(A4))
    width, height = landscape(A4)

    # --- DESIGN DO CERTIFICADO ---
    # Fundo moderno escuro (Navy / Dark Slate)
    p.setFillColor(colors.HexColor('#0F172A'))
    p.rect(0, 0, width, height, fill=True, stroke=False)

    # Moldura externa em Ciano
    p.setStrokeColor(colors.HexColor('#06B6D4'))
    p.setLineWidth(3)
    p.rect(24, 24, width - 48, height - 48, fill=False, stroke=True)

    # Moldura interna sutil em Esmeralda
    p.setStrokeColor(colors.HexColor('#10B981'))
    p.setLineWidth(1)
    p.rect(30, 30, width - 60, height - 60, fill=False, stroke=True)

    # Cantoneiras decorativas tech
    p.setFillColor(colors.HexColor('#38BDF8'))
    for cx, cy in [(24, 24), (width-24, 24), (24, height-24), (width-24, height-24)]:
        p.circle(cx, cy, 4, fill=True, stroke=False)

    # Logo / Badge Superior
    p.setFillColor(colors.HexColor('#06B6D4'))
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2.0, height - 70, "</> CODEVIEW")

    p.setFillColor(colors.HexColor('#94A3B8'))
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(width / 2.0, height - 88, "PLATAFORMA DE MICROAPRENDIZAGEM & PORTFÓLIO VIVO")

    # Linha separadora decorativa superior
    p.setStrokeColor(colors.HexColor('#1E293B'))
    p.setLineWidth(1)
    p.line(width/2.0 - 150, height - 98, width/2.0 + 150, height - 98)

    # Título do Certificado
    p.setFillColor(colors.HexColor('#38BDF8'))
    p.setFont("Helvetica-Bold", 26)
    p.drawCentredString(width / 2.0, height - 135, "CERTIFICADO DE CONCLUSÃO")

    # Texto de introdução
    p.setFillColor(colors.HexColor('#94A3B8'))
    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2.0, height - 170, "Certificamos para fins de comprovação técnica no Portfólio Vivo que")

    # Nome do Aluno
    student_name = student.get_full_name() or student.first_name or student.username
    p.setFillColor(colors.HexColor('#FFFFFF'))
    p.setFont("Helvetica-Bold", 28)
    p.drawCentredString(width / 2.0, height - 215, student_name)

    # Linha de destaque sob o nome
    p.setStrokeColor(colors.HexColor('#06B6D4'))
    p.setLineWidth(2)
    text_width = p.stringWidth(student_name, "Helvetica-Bold", 28)
    line_w = max(text_width + 40, 260)
    p.line(width/2.0 - line_w/2.0, height - 225, width/2.0 + line_w/2.0, height - 225)

    # Texto descritivo de conclusão
    p.setFillColor(colors.HexColor('#CBD5E1'))
    p.setFont("Helvetica", 12)
    p.drawCentredString(
        width / 2.0,
        height - 255,
        "concluiu com êxito todas as aulas práticas e desafios técnicos da trilha de conhecimento:"
    )

    # Nome do Curso
    p.setFillColor(colors.HexColor('#22D3EE'))
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2.0, height - 290, course.title)

    # Metadados do Curso (Tecnologia, Nível, Carga Horária)
    tech_name = course.technology.name if course.technology else "Programação"
    level_display = course.get_level_display()
    workload = f"{course.estimated_minutes} min ({course.total_lessons} pílulas)"
    metadata_text = f"Tecnologia: {tech_name}   |   Nível: {level_display}   |   Carga Horária: {workload}"
    p.setFillColor(colors.HexColor('#94A3B8'))
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2.0, height - 315, metadata_text)

    # Bloco Inferior: Instrutor, Data & Código de Autenticidade + QR Code
    y_footer = 85

    # Coluna 1: Instrutor
    p.setStrokeColor(colors.HexColor('#334155'))
    p.setLineWidth(1)
    p.line(70, y_footer + 50, 260, y_footer + 50)
    instructor_name = instructor.get_full_name() or instructor.first_name or instructor.username
    p.setFillColor(colors.HexColor('#FFFFFF'))
    p.setFont("Helvetica-Bold", 10)
    p.drawString(70, y_footer + 36, instructor_name)
    p.setFillColor(colors.HexColor('#64748B'))
    p.setFont("Helvetica", 8)
    p.drawString(70, y_footer + 24, "Mentor / Instrutor Responsável")

    # Coluna 2: Data de Emissão & Código de Autenticidade
    issue_date_str = certificate.issued_at.strftime('%d/%m/%Y às %H:%M')
    p.setFillColor(colors.HexColor('#94A3B8'))
    p.setFont("Helvetica-Bold", 9)
    p.drawString(300, y_footer + 46, f"Data de Emissão: {issue_date_str}")
    p.setFillColor(colors.HexColor('#10B981'))
    p.setFont("Helvetica-Bold", 10)
    p.drawString(300, y_footer + 30, f"Autenticidade: {certificate.validation_code}")
    p.setFillColor(colors.HexColor('#64748B'))
    p.setFont("Helvetica", 8)
    p.drawString(300, y_footer + 16, "Validação pública via CodeView Authenticity Engine")

    # Coluna 3: QR Code embutido
    p.drawImage(
        ImageReader(qr_buf),
        width - 170,
        y_footer + 5,
        width=70,
        height=70
    )
    p.setFillColor(colors.HexColor('#94A3B8'))
    p.setFont("Helvetica", 7)
    p.drawCentredString(width - 135, y_footer - 4, "Escaneie para validar")

    p.showPage()
    p.save()
    buf.seek(0)

    response = HttpResponse(buf.getvalue(), content_type='application/pdf')
    filename = f"certificado_codeview_{certificate.validation_code}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def my_courses_view(request):
    """
    Lista os mini-cursos criados e instruídos pelo usuário logado,
    permitindo gerenciar e editar suas trilhas, vídeos e desafios.
    """
    courses = Course.objects.filter(instructor=request.user).select_related('technology').prefetch_related('lessons', 'enrollments').order_by('-created_at')
    return render(request, 'courses/my_courses.html', {
        'courses': courses,
    })


@login_required
def course_create_view(request):
    """
    Criação dinâmica de novos mini-cursos por qualquer usuário da plataforma.
    Permite configurar os dados do curso, cronograma personalizado e adicionar pílulas de vídeo.
    """
    technologies = Technology.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        technology_id = request.POST.get('technology')
        level = request.POST.get('level', 'iniciante')
        estimated_minutes = request.POST.get('estimated_minutes', '30')
        custom_schedule = request.POST.get('custom_schedule', '').strip()
        thumbnail = request.FILES.get('thumbnail')

        if not title:
            messages.error(request, "O título da trilha é obrigatório.")
        elif not description:
            messages.error(request, "A descrição da trilha é obrigatória.")
        else:
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            tech = Technology.objects.filter(id=technology_id).first() if technology_id else None

            try:
                est_min = max(5, int(estimated_minutes))
            except ValueError:
                est_min = 30

            course = Course.objects.create(
                title=title,
                slug=slug,
                description=description,
                technology=tech,
                instructor=request.user,
                level=level if level in dict(Course.LEVEL_CHOICES) else 'iniciante',
                estimated_minutes=est_min,
                custom_schedule=custom_schedule,
                thumbnail=thumbnail,
                is_published=True
            )

            # Promove o perfil a criador/mentor automaticamente caso ainda não seja
            if hasattr(request.user, 'profile') and not request.user.profile.is_mentor:
                request.user.profile.is_mentor = True
                request.user.profile.save()

            # Notifica o usuário criador da trilha
            Notification.objects.create(
                user=request.user,
                title="📚 Nova Trilha Criada com Sucesso!",
                message=f"Sua trilha '{course.title}' foi cadastrada! Agora você pode gerenciar e adicionar aulas, pílulas de vídeo e desafios práticos.",
                link=reverse('course_manage', kwargs={'slug': course.slug}),
                icon='🚀'
            )

            messages.success(request, f"Trilha '{course.title}' criada com sucesso! Agora configure as aulas, vídeos e desafios.")
            return redirect('course_manage', slug=course.slug)

    return render(request, 'courses/course_create.html', {
        'technologies': technologies,
        'levels': Course.LEVEL_CHOICES,
    })


@login_required
def course_manage_view(request, slug):
    """
    Painel de gerenciamento completo do criador para um Mini-Curso:
    - Edição dos dados do curso (título, ementa, cronograma personalizado, nível, capa)
    - Lista de pílulas/aulas cadastradas com ordem, vídeo associado e status do desafio
    - Ações dinâmicas para adicionar, editar, reordenar ou remover aulas e mini-atividades.
    """
    course = get_object_or_404(Course, slug=slug)

    # Permissão: apenas o autor/instrutor do curso ou superuser
    if request.user != course.instructor and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para gerenciar este curso.")
        return redirect('course_detail', slug=course.slug)

    technologies = Technology.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        action = request.POST.get('action', 'update_course')
        if action == 'update_course':
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            technology_id = request.POST.get('technology')
            level = request.POST.get('level', course.level)
            estimated_minutes = request.POST.get('estimated_minutes', str(course.estimated_minutes))
            custom_schedule = request.POST.get('custom_schedule', '').strip()
            is_published = request.POST.get('is_published') == 'on'

            if not title:
                messages.error(request, "O título do curso não pode ficar vazio.")
            elif not description:
                messages.error(request, "A descrição do curso não pode ficar vazia.")
            else:
                course.title = title
                course.description = description
                course.level = level if level in dict(Course.LEVEL_CHOICES) else course.level
                try:
                    course.estimated_minutes = max(5, int(estimated_minutes))
                except ValueError:
                    pass
                course.custom_schedule = custom_schedule
                course.is_published = is_published

                if technology_id:
                    course.technology = Technology.objects.filter(id=technology_id).first()

                if 'thumbnail' in request.FILES:
                    course.thumbnail = request.FILES['thumbnail']

                course.save()
                messages.success(request, "Dados da trilha atualizados com sucesso!")
                return redirect('course_manage', slug=course.slug)

    lessons = course.lessons.select_related('video', 'challenge').order_by('order', 'id')
    user_videos = Video.objects.filter(author=request.user).order_by('-created_at')

    total_enrollments = Enrollment.objects.filter(course=course, is_active=True).count()
    completed_enrollments = Enrollment.objects.filter(course=course, completed_at__isnull=False).count()
    total_challenges = sum(1 for l in lessons if hasattr(l, 'challenge') and l.challenge is not None)

    return render(request, 'courses/course_manage.html', {
        'course': course,
        'lessons': lessons,
        'user_videos': user_videos,
        'technologies': technologies,
        'levels': Course.LEVEL_CHOICES,
        'total_enrollments': total_enrollments,
        'completed_enrollments': completed_enrollments,
        'total_challenges': total_challenges,
    })


@login_required
def lesson_create_view(request, slug):
    """
    Adiciona dinamicamente uma nova aula / pílula a uma trilha existente.
    Permite subir arquivo de vídeo próprio (com validação estrita sem imagens),
    vincular pílula do feed e cadastrar mini-atividade interativa vinculada.
    """
    course = get_object_or_404(Course, slug=slug)

    if request.user != course.instructor and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para adicionar aulas a este curso.")
        return redirect('course_detail', slug=course.slug)

    user_videos = Video.objects.filter(author=request.user).order_by('-created_at')
    next_order = course.lessons.count() + 1

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        duration_seconds = request.POST.get('duration_seconds', '60')
        order = request.POST.get('order', str(next_order))
        existing_video_id = request.POST.get('existing_video')
        video_file = request.FILES.get('video_file')

        if not title:
            messages.error(request, "O título da aula é obrigatório.")
            return render(request, 'courses/lesson_form.html', {
                'course': course,
                'user_videos': user_videos,
                'next_order': next_order,
                'is_edit': False,
            })

        try:
            dur = max(5, int(duration_seconds))
        except ValueError:
            dur = 60

        try:
            ord_num = max(1, int(order))
        except ValueError:
            ord_num = next_order

        # Processamento de vídeo
        video_obj = None
        if video_file:
            try:
                validate_video_file(video_file)
            except ValidationError as e:
                messages.error(request, f"Arquivo de vídeo inválido: {e.message}")
                return render(request, 'courses/lesson_form.html', {
                    'course': course,
                    'user_videos': user_videos,
                    'next_order': next_order,
                    'is_edit': False,
                })

            video_obj = Video.objects.create(
                title=f"{course.title}: {title}",
                description=content or f"Pílula prática da trilha {course.title}.",
                video_file=video_file,
                technology=course.technology or Technology.objects.first(),
                author=request.user,
                duration_seconds=dur,
                is_published=True
            )
        elif existing_video_id:
            video_obj = Video.objects.filter(id=existing_video_id, author=request.user).first()

        lesson = Lesson.objects.create(
            course=course,
            title=title,
            content=content,
            duration_seconds=dur,
            order=ord_num,
            video=video_obj
        )

        # Cadastro opcional de mini-atividade (desafio) se preenchido na mesma tela
        challenge_title = request.POST.get('challenge_title', '').strip()
        question_text = request.POST.get('question_text', '').strip()
        option_a = request.POST.get('option_a', '').strip()
        option_b = request.POST.get('option_b', '').strip()
        option_c = request.POST.get('option_c', '').strip()
        option_d = request.POST.get('option_d', '').strip()
        correct_option = request.POST.get('correct_option', 'A')
        code_snippet = request.POST.get('code_snippet', '').strip()
        explanation = request.POST.get('explanation', '').strip()
        points = request.POST.get('points', '10')

        if challenge_title and question_text and option_a and option_b:
            try:
                pts = max(1, int(points))
            except ValueError:
                pts = 10

            Challenge.objects.create(
                lesson=lesson,
                title=challenge_title,
                question_text=question_text,
                code_snippet=code_snippet,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c or 'N.D.A.',
                option_d=option_d,
                correct_option=correct_option if correct_option in ['A', 'B', 'C', 'D'] else 'A',
                explanation=explanation or 'Resposta validada pelo instrutor.',
                points=pts
            )

        messages.success(request, f"Aula '{lesson.title}' adicionada com sucesso à trilha!")
        return redirect('course_manage', slug=course.slug)

    return render(request, 'courses/lesson_form.html', {
        'course': course,
        'user_videos': user_videos,
        'next_order': next_order,
        'is_edit': False,
    })


@login_required
def lesson_edit_view(request, slug, lesson_id):
    """
    Edição de uma aula / pílula existente na trilha pelo criador.
    """
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    if request.user != course.instructor and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para editar esta aula.")
        return redirect('course_detail', slug=course.slug)

    user_videos = Video.objects.filter(author=request.user).order_by('-created_at')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        duration_seconds = request.POST.get('duration_seconds', str(lesson.duration_seconds))
        order = request.POST.get('order', str(lesson.order))
        existing_video_id = request.POST.get('existing_video')
        video_file = request.FILES.get('video_file')

        if not title:
            messages.error(request, "O título da aula é obrigatório.")
        else:
            try:
                lesson.duration_seconds = max(5, int(duration_seconds))
            except ValueError:
                pass

            try:
                lesson.order = max(1, int(order))
            except ValueError:
                pass

            lesson.title = title
            lesson.content = content

            # Atualização de vídeo
            if video_file:
                try:
                    validate_video_file(video_file)
                except ValidationError as e:
                    messages.error(request, f"Arquivo de vídeo inválido: {e.message}")
                    return render(request, 'courses/lesson_form.html', {
                        'course': course,
                        'lesson': lesson,
                        'user_videos': user_videos,
                        'next_order': lesson.order,
                        'is_edit': True,
                    })

                new_video = Video.objects.create(
                    title=f"{course.title}: {title}",
                    description=content or f"Pílula prática da trilha {course.title}.",
                    video_file=video_file,
                    technology=course.technology or Technology.objects.first(),
                    author=request.user,
                    duration_seconds=lesson.duration_seconds,
                    is_published=True
                )
                lesson.video = new_video
            elif existing_video_id:
                sel_video = Video.objects.filter(id=existing_video_id, author=request.user).first()
                if sel_video:
                    lesson.video = sel_video

            lesson.save()
            messages.success(request, f"Aula '{lesson.title}' atualizada com sucesso!")
            return redirect('course_manage', slug=course.slug)

    return render(request, 'courses/lesson_form.html', {
        'course': course,
        'lesson': lesson,
        'user_videos': user_videos,
        'next_order': lesson.order,
        'is_edit': True,
    })


@login_required
def lesson_delete_view(request, slug, lesson_id):
    """
    Exclui uma aula da trilha e reordena as aulas subsequentes.
    """
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    if request.user != course.instructor and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para excluir esta aula.")
        return redirect('course_detail', slug=course.slug)

    if request.method == 'POST':
        title = lesson.title
        lesson.delete()

        # Reordenação contínua das aulas restantes
        for idx, l in enumerate(course.lessons.all().order_by('order', 'id'), start=1):
            if l.order != idx:
                l.order = idx
                l.save(update_fields=['order'])

        messages.success(request, f"Aula '{title}' excluída da trilha.")
        return redirect('course_manage', slug=course.slug)

    return render(request, 'courses/lesson_confirm_delete.html', {
        'course': course,
        'lesson': lesson,
    })


@login_required
def lesson_reorder_view(request, slug, lesson_id, direction):
    """
    Ajusta a sequência pedagógica da aula na trilha (subir ou descer).
    """
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    if request.user != course.instructor and not request.user.is_superuser:
        messages.error(request, "Sem permissão para alterar ordem.")
        return redirect('course_detail', slug=course.slug)

    lessons = list(course.lessons.all().order_by('order', 'id'))
    try:
        curr_idx = lessons.index(lesson)
    except ValueError:
        return redirect('course_manage', slug=course.slug)

    if direction == 'up' and curr_idx > 0:
        prev_lesson = lessons[curr_idx - 1]
        prev_order = prev_lesson.order
        prev_lesson.order = lesson.order
        lesson.order = prev_order
        lesson.save(update_fields=['order'])
        prev_lesson.save(update_fields=['order'])
        messages.success(request, f"Aula '{lesson.title}' movida para cima.")
    elif direction == 'down' and curr_idx < len(lessons) - 1:
        next_lesson = lessons[curr_idx + 1]
        next_order = next_lesson.order
        next_lesson.order = lesson.order
        lesson.order = next_order
        lesson.save(update_fields=['order'])
        next_lesson.save(update_fields=['order'])
        messages.success(request, f"Aula '{lesson.title}' movida para baixo.")

    return redirect('course_manage', slug=course.slug)


@login_required
def challenge_manage_view(request, slug, lesson_id):
    """
    Lista todos os desafios práticos da aula para o criador, permitindo
    adicionar quantos desafios desejar (discursivos ou alternativas).
    """
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    if request.user != course.instructor and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para gerenciar desafios deste curso.")
        return redirect('course_detail', slug=course.slug)

    challenges = lesson.challenges.all().order_by('order', 'id')
    if not challenges.exists():
        # Se ainda não possui nenhum desafio, encaminha direto para a tela de criação
        return redirect('challenge_create', slug=course.slug, lesson_id=lesson.id)

    return render(request, 'courses/challenge_list.html', {
        'course': course,
        'lesson': lesson,
        'challenges': challenges,
    })


@login_required
def challenge_create_view(request, slug, lesson_id):
    """
    Cria um novo desafio prático para a aula (Múltipla Escolha ou Discursiva).
    """
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    if request.user != course.instructor and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para adicionar desafios.")
        return redirect('course_detail', slug=course.slug)

    if request.method == 'POST':
        challenge_type = request.POST.get('challenge_type', 'alternativa')
        title = request.POST.get('title', '').strip()
        question_text = request.POST.get('question_text', '').strip()
        code_snippet = request.POST.get('code_snippet', '').strip()
        points = request.POST.get('points', '10')
        explanation = request.POST.get('explanation', '').strip()

        # Alternativas
        option_a = request.POST.get('option_a', '').strip()
        option_b = request.POST.get('option_b', '').strip()
        option_c = request.POST.get('option_c', '').strip()
        option_d = request.POST.get('option_d', '').strip()
        correct_option = request.POST.get('correct_option', 'A')

        # Discursiva
        expected_answer = request.POST.get('expected_answer', '').strip()
        expected_code_keyword = request.POST.get('expected_code_keyword', '').strip()

        if not title or not question_text:
            messages.error(request, "Título e enunciado da questão são obrigatórios.")
        elif challenge_type == 'alternativa' and (not option_a or not option_b):
            messages.error(request, "Para questões de alternativas, forneça pelo menos as opções A e B.")
        else:
            try:
                pts = max(1, int(points))
            except ValueError:
                pts = 10

            next_order = lesson.challenges.count() + 1
            Challenge.objects.create(
                lesson=lesson,
                challenge_type=challenge_type if challenge_type in ['alternativa', 'discursiva'] else 'alternativa',
                title=title,
                order=next_order,
                question_text=question_text,
                code_snippet=code_snippet,
                option_a=option_a,
                option_b=option_b,
                option_c=option_c,
                option_d=option_d,
                correct_option=correct_option if correct_option in ['A', 'B', 'C', 'D'] else 'A',
                expected_answer=expected_answer,
                expected_code_keyword=expected_code_keyword,
                explanation=explanation or 'Resposta correta conforme verificação técnica do instrutor.',
                points=pts
            )
            messages.success(request, f"Desafio '{title}' adicionado à aula {lesson.order} com sucesso!")
            return redirect('challenge_manage', slug=course.slug, lesson_id=lesson.id)

    return render(request, 'courses/challenge_form.html', {
        'course': course,
        'lesson': lesson,
        'challenge': None,
        'is_edit': False,
    })


@login_required
def challenge_edit_view(request, slug, lesson_id, challenge_id):
    """
    Edita um desafio prático existente na aula.
    """
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    challenge = get_object_or_404(Challenge, id=challenge_id, lesson=lesson)

    if request.user != course.instructor and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para editar este desafio.")
        return redirect('course_detail', slug=course.slug)

    if request.method == 'POST':
        challenge_type = request.POST.get('challenge_type', challenge.challenge_type)
        title = request.POST.get('title', '').strip()
        question_text = request.POST.get('question_text', '').strip()
        code_snippet = request.POST.get('code_snippet', '').strip()
        points = request.POST.get('points', str(challenge.points))
        explanation = request.POST.get('explanation', '').strip()

        option_a = request.POST.get('option_a', '').strip()
        option_b = request.POST.get('option_b', '').strip()
        option_c = request.POST.get('option_c', '').strip()
        option_d = request.POST.get('option_d', '').strip()
        correct_option = request.POST.get('correct_option', 'A')

        expected_answer = request.POST.get('expected_answer', '').strip()
        expected_code_keyword = request.POST.get('expected_code_keyword', '').strip()

        if not title or not question_text:
            messages.error(request, "Título e enunciado da questão são obrigatórios.")
        else:
            try:
                challenge.points = max(1, int(points))
            except ValueError:
                pass

            challenge.challenge_type = challenge_type if challenge_type in ['alternativa', 'discursiva'] else challenge.challenge_type
            challenge.title = title
            challenge.question_text = question_text
            challenge.code_snippet = code_snippet
            challenge.option_a = option_a
            challenge.option_b = option_b
            challenge.option_c = option_c
            challenge.option_d = option_d
            challenge.correct_option = correct_option if correct_option in ['A', 'B', 'C', 'D'] else challenge.correct_option
            challenge.expected_answer = expected_answer
            challenge.expected_code_keyword = expected_code_keyword
            challenge.explanation = explanation
            challenge.save()

            messages.success(request, f"Desafio '{challenge.title}' atualizado com sucesso!")
            return redirect('challenge_manage', slug=course.slug, lesson_id=lesson.id)

    return render(request, 'courses/challenge_form.html', {
        'course': course,
        'lesson': lesson,
        'challenge': challenge,
        'is_edit': True,
    })


@login_required
def challenge_delete_view(request, slug, lesson_id, challenge_id):
    """
    Exclui um desafio prático de uma aula e reordena os desafios restantes.
    """
    course = get_object_or_404(Course, slug=slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    challenge = get_object_or_404(Challenge, id=challenge_id, lesson=lesson)

    if request.user != course.instructor and not request.user.is_superuser:
        messages.error(request, "Você não tem permissão para excluir este desafio.")
        return redirect('course_detail', slug=course.slug)

    if request.method == 'POST':
        title = challenge.title
        challenge.delete()

        # Reordena os desafios restantes da aula
        for idx, ch in enumerate(lesson.challenges.all().order_by('order', 'id'), start=1):
            if ch.order != idx:
                ch.order = idx
                ch.save(update_fields=['order'])

        messages.success(request, f"Desafio '{title}' excluído da aula.")
        return redirect('challenge_manage', slug=course.slug, lesson_id=lesson.id)

    return render(request, 'courses/challenge_confirm_delete.html', {
        'course': course,
        'lesson': lesson,
        'challenge': challenge,
    })


