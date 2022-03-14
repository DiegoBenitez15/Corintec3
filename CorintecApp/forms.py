from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

class CustomUserCreationForm(UserCreationForm):
    pass

class AgregarProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'

class AgregarClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AgregarClienteForm, self).__init__(*args, **kwargs)
        self.fields['RNC'].label = 'RNC'

class AgregarDistribuidorForm(forms.ModelForm):
    class Meta:
        model = Distribuidor
        fields = '__all__'

    def save(self, commit=True):
        reporte = super().save(commit=False)

        if commit:
            reporte.save()

        return reporte