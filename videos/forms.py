from django import forms
from .models import Video, Technology


class VideoPublishForm(forms.ModelForm):
    """
    Formulário para publicação de novos micro-vídeos verticais (9:16) no Feed (Onda 3).
    """
    class Meta:
        model = Video
        fields = ['title', 'technology', 'description', 'video_file', 'duration_seconds']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Ex: Python: List Comprehension em 30 segundos',
                'class': 'w-full px-4 py-3 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:border-cyan-500 focus:outline-none',
            }),
            'technology': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:border-cyan-500 focus:outline-none',
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Resumo rápido ou snippet de código explicado no vídeo...',
                'class': 'w-full px-4 py-3 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:border-cyan-500 focus:outline-none',
            }),
            'duration_seconds': forms.NumberInput(attrs={
                'min': 5,
                'max': 180,
                'class': 'w-full px-4 py-3 rounded-xl bg-gray-900 border border-gray-700 text-white text-sm focus:border-cyan-500 focus:outline-none',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['technology'].queryset = Technology.objects.filter(is_active=True).order_by('name')

