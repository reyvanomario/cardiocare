from django import forms
from .models import Dokter

class DokterForm(forms.ModelForm):
    class Meta:
        model = Dokter
        fields = ['kuota'] 
        labels = {
            'kuota': 'Kuota Pasien'
        }
        widgets = {
            'kuota': forms.NumberInput(attrs={'class': 'form-control'})
        }