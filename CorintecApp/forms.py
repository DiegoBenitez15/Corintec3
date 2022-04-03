from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()

class UserCreationFormCustom(UserCreationForm):
    error_messages = {'password_mismatch': ("Las dos contraseñas no coinciden."),}

    def __init__(self, *args, **kwargs):
        super(UserCreationFormCustom, self).__init__(*args, **kwargs)

        self.fields['password2'].label = 'Confirmación de contraseña'
        self.fields['username'].label = 'Usuario'
        self.fields['username'].help_text = 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.'
        self.fields['password1'].help_text = """<ul><li>Tu contraseña no puede ser similar a tu otra información personal.</li><li>Tu contraseña debe tener por lo menos 8 caracteres.</li><li>Tu contraseña no puede ser una comúnmente usada.</li><li>Tu contraseña no puede ser numérico completamente.</li></ul>"""
        self.fields['password2'].help_text = 'Entre la misma contraseña que antes, para verificación.'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}

class AgregarProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'

class RegistrarForm(forms.ModelForm):
    class Meta:
        model = Empleados
        fields = '__all__'
        exclude = ['carrito']

class AgregarClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = '__all__'
        exclude = ['estado']

    def __init__(self, *args, **kwargs):
        super(AgregarClienteForm, self).__init__(*args, **kwargs)
        self.fields['rnc'].label = 'RNC'

class AgregarDistribuidorForm(forms.ModelForm):
    class Meta:
        model = Distribuidor
        fields = '__all__'
        exclude = ['estado']

    def save(self, commit=True):
        reporte = super().save(commit=False)

        if commit:
            reporte.save()

        return reporte
    
    
class CreateAdminUsuarioForm(forms.ModelForm):

    class Meta:
        model = AdministradorUsuario
        fields = ['nombre','apellido','identificacion','correo','genero','telefono']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(CreateAdminUsuarioForm, self).__init__(*args, **kwargs)

    def save(self, commit=False):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class RegistrarFacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['cliente','tipoPago']

    def __init__(self, *args, **kwargs):
        super(RegistrarFacturaForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        factura = super().save(commit=True)
        carrito_id = self.initial['carrito_id']
        carrito = CarritoCompras.objects.get(pk=carrito_id)

        if commit:
            factura.totalPago = carrito.total
            factura.subTotal = carrito.subtotal
            factura.ITBIS = carrito.itbis

            for i in carrito.carrito_productos.all():
                factura.productos.add(i)

            factura.save()
            carrito.carrito_productos.clear()
            carrito.actualizarPrecios()
        return factura



