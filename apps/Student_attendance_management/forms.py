from django import forms
from .models import Batch

class BatchForm(forms.ModelForm):

    class Meta:
        model = Batch
        fields = [
            'batch_name',
            'course',
            'timing',
            'start_time',
            'end_time',
            'start_date',
            'end_date',
            'trainer',
        ]

        widgets = {
            'batch_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Eg: June 2026',
            }),

            'course': forms.Select(attrs={
                'class': 'form-select'
            }),

            'timing': forms.Select(attrs={
                'class': 'form-control'
            }),

            'start_date':forms.DateInput(attrs={
                'class':'form-control',
                'type':'date'
            }),

            'end_date':forms.DateInput(attrs={
                'class':'form-control',
                'type':'date'
            }),

            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),

            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),

            'trainer': forms.Select(attrs={
                'class': 'form-select'
            }),
        }