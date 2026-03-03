from django import forms
from apps.core.models import Brigada

class BrigadaForm(forms.ModelForm):
    class Meta:
        model = Brigada
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Número de la brigada...',
                'class': 'modal-input'
            })
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre.isdigit():
            raise forms.ValidationError("El nombre debe ser un número entero (ej: 1, 2, 3).")
        return nombre