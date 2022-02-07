from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

class CustomUserCreationForm(UserCreationForm):
    pass

class AgregarClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'

    def save(self, commit=True):
        reporte = super().save(commit=False)

        if commit:
            reporte.save()

        return reporte

class AgregarDistribuidorForm(forms.ModelForm):
    class Meta:
        model = Distribuidor
        fields = '__all__'

    def save(self, commit=True):
        reporte = super().save(commit=False)

        if commit:
            reporte.save()

        return reporte