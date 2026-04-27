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

    def __init__(self, *args, **kwargs):
        # Extraemos el periodo para validarlo internamente
        self.periodo = kwargs.pop('periodo', None)
        super().__init__(*args, **kwargs)

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre.isdigit():
            raise forms.ValidationError("El nombre debe ser un número entero.")

        # Validación de existencia única en este periodo
        if self.periodo and Brigada.objects.filter(periodo=self.periodo, nombre=nombre).exists():
            raise forms.ValidationError(
                f"La Brigada #{nombre} ya existe en este periodo.")

        return nombre
