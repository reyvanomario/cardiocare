from django import forms
from .models import Dokter

class UpdateKuotaDokterForm(forms.ModelForm):
    class Meta:
        model = Dokter
        fields = ['kuota']
        widgets = {
            'kuota': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            })
        }