from django import forms
from .models import ConsultationRecord

class ConsultationRecordForm(forms.ModelForm):
    class Meta:
        model = ConsultationRecord
        fields = ['diagnosis', 'notes', 'prescription', 'requested_tests']
        widgets = {
            'diagnosis': forms.Textarea(attrs={
                'class': 'med-input',
                'rows': 3,
                'placeholder': 'Enter diagnosis...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'med-input',
                'rows': 4,
                'placeholder': 'Write consultation notes...'
            }),
            'prescription': forms.Textarea(attrs={
                'class': 'med-input',
                'rows': 3,
                'placeholder': 'Enter prescribed medication...'
            }),
            'requested_tests': forms.Textarea(attrs={
                'class': 'med-input',
                'rows': 3,
                'placeholder': 'List requested lab tests...'
            }),
        }