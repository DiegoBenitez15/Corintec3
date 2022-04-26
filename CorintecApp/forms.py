from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db import models
from django.utils import timezone
import datetime

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
        exclude = ['cantidad','precio_venta','estado','codigo']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(AgregarProductoForm, self).__init__(*args, **kwargs)
        self.fields['registrado_por'].initial = user
        self.fields['registrado_por'].disabled = True

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
        exclude = ['carrito','productos']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(CreateAdminUsuarioForm, self).__init__(*args, **kwargs)
        self.fields['usuario'].initial = user
        self.fields['usuario'].disabled = True

class CreateVendedorUsuarioForm(forms.ModelForm):
    class Meta:
        model = VendedorUsuario
        exclude = ['carrito','productos']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(CreateVendedorUsuarioForm, self).__init__(*args, **kwargs)
        self.fields['usuario'].initial = user
        self.fields['usuario'].disabled = True

class RegistrarFacturaForm(forms.ModelForm):
    fecha_envio = forms.DateField()

    class Meta:
        model = Factura
        fields = ['cliente','tipoPago']

    def __init__(self, *args, **kwargs):
        super(RegistrarFacturaForm, self).__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(pk=self.initial['cliente'])

    def clean(self):
        cleaned_data = super().clean()
        fecha_envio = cleaned_data.get("fecha_envio")
       
        if fecha_envio < datetime.datetime.date(timezone.now()):
            raise forms.ValidationError({
                'fecha_envio': ["La fecha tiene que ser de hoy en adelante", ],
            })

    def save(self, commit=True):
        factura = super().save(commit=True)
        carrito_id = self.initial['carrito_id']
        carrito = CarritoCompras.objects.get(pk=carrito_id)
        fecha_envio = self.cleaned_data['fecha_envio']

        if commit:
            factura.totalPago = carrito.total
            factura.subTotal = carrito.subtotal
            factura.ITBIS = carrito.itbis

            for i in carrito.producto_add.all():
                producto = Producto.objects.get(pk = i.producto.pk)
                producto.cantidad -= i.cantidad
                producto.save()
                i.precio_venta = producto.precio_venta
                i.save()
                factura.productos.add(i)

            factura.save()
            orden_envio = OrdenEnvio.objects.create(registrado_por=self.initial['user'],estadoEnvio=0,fecha_envio=fecha_envio)
            orden_envio.save()
            pedido = Pedido.objects.create(factura=factura, orden_envio=orden_envio)
            pedido.save()
            carrito.producto_add.clear()
            carrito.actualizarPrecios()
        return factura

class RegistrarOrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = ['distribuidor']

    distribuidor = models.ForeignKey(Distribuidor, on_delete=models.CASCADE, null=True)
    estado = models.PositiveIntegerField(choices=t_estadoOrdenCompra, null=True)

    def __init__(self, *args, **kwargs):
        super(RegistrarOrdenCompraForm, self).__init__(*args, **kwargs)
        self.fields['distribuidor'].queryset = Distribuidor.objects.filter(pk=self.initial['distribuidor'])

    def save(self, commit=True):
        factura = super().save(commit=True)
        carrito_id = self.initial['carrito_id']
        carrito = CarritoCompras.objects.get(pk=carrito_id)
        factura.recibido_por = self.initial['user']
        factura.estado = 0

        if commit:
            factura.totalPago = carrito.total
            factura.subTotal = carrito.subtotal
            factura.ITBIS = carrito.itbis

            for i in carrito.producto_add.all():
                factura.productos.add(i)

            factura.save()
            carrito.producto_add.clear()
            carrito.actualizarPrecios()
        return factura

CHOICES_PRIVACIDAD = [(1, 'SI'),(0, 'NO'),]

class CreateDevolucionesForm(forms.ModelForm):

    class Meta:
        model = Devoluciones
        exclude = ['fecha_registro']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        factura = kwargs.pop('factura')
        super(CreateDevolucionesForm, self).__init__(*args, **kwargs)
        self.fields['registrado_por'].initial = user
        self.fields['registrado_por'].disabled = True
        self.fields['factura'].initial = factura
        self.fields['factura'].disabled = True

    def save(self, commit=True):
        devolucion = super().save(commit=True)
        if commit:
            productos = devolucion.factura.productos

            if devolucion.producto_a_inventario == 1:
                for i in productos.all():
                    i.producto.cantidad = i.producto.cantidad + i.cantidad
                    i.producto.save()

            devolucion.save()
        return devolucion

