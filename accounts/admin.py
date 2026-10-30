from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, UserConsent, DirectMessage, Notification, TAMEvaluation


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Perfil'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'username')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password'),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_mentor', 'specialties', 'created_at', 'updated_at')
    list_filter = ('is_mentor',)
    search_fields = ('user__email', 'bio', 'specialties')


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__email', 'recipient__email', 'content')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'icon', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')


@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    list_display = ('user', 'terms_version', 'accepted_at', 'ip_address')
    list_filter = ('terms_version', 'accepted_at')
    search_fields = ('user__email', 'ip_address')
    readonly_fields = ('user', 'terms_version', 'accepted_at', 'ip_address')


@admin.register(TAMEvaluation)
class TAMEvaluationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_name_display', 'role', 'experience', 'device',
        'display_pu', 'display_peou', 'display_atu', 'display_biu', 'display_overall',
        'created_at'
    )
    list_filter = ('role', 'experience', 'device', 'created_at')
    search_fields = ('evaluator_name', 'evaluator_email', 'highlights', 'difficulties', 'suggestions')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Identificação do Avaliador', {
            'fields': ('user', 'evaluator_name', 'evaluator_email', 'role', 'experience', 'device', 'created_at')
        }),
        ('Utilidade Percebida (PU - Escala 1 a 5)', {
            'fields': ('pu1', 'pu2', 'pu3', 'pu4', 'pu5')
        }),
        ('Facilidade de Uso Percebida (PEOU - Escala 1 a 5)', {
            'fields': ('peou1', 'peou2', 'peou3', 'peou4', 'peou5')
        }),
        ('Atitude em Relação ao Uso (ATU - Escala 1 a 5)', {
            'fields': ('atu1', 'atu2', 'atu3')
        }),
        ('Intenção Comportamental de Uso (BIU - Escala 1 a 5)', {
            'fields': ('biu1', 'biu2', 'biu3')
        }),
        ('Avaliação Qualitativa Aberta', {
            'fields': ('highlights', 'difficulties', 'suggestions')
        }),
    )

    def get_name_display(self, obj):
        return obj.evaluator_name or (obj.user.email if obj.user else "Anônimo")
    get_name_display.short_description = "Avaliador"

    def display_pu(self, obj):
        return f"{obj.pu_score:.2f}"
    display_pu.short_description = "Média PU"

    def display_peou(self, obj):
        return f"{obj.peou_score:.2f}"
    display_peou.short_description = "Média PEOU"

    def display_atu(self, obj):
        return f"{obj.atu_score:.2f}"
    display_atu.short_description = "Média ATU"

    def display_biu(self, obj):
        return f"{obj.biu_score:.2f}"
    display_biu.short_description = "Média BIU"

    def display_overall(self, obj):
        return f"⭐ {obj.overall_score:.2f}"
    display_overall.short_description = "Índice TAM Geral"

