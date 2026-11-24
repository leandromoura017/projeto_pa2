from django import forms
from .models import Video, Technology, validate_video_file


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
            'video_file': forms.FileInput(attrs={
                'accept': 'video/mp4,video/webm,video/quicktime,video/x-matroska,video/*',
                'class': 'w-full text-xs text-gray-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-cyan-600 file:text-white hover:file:bg-cyan-500 cursor-pointer',
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

    def clean_video_file(self):
        file = self.cleaned_data.get('video_file')
        if file:
            validate_video_file(file)
        return file


