from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import *
from .models import *
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from .decorators import *
from django.contrib.auth.decorators import login_required

# Create your views here.

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class home(ListView):
    template_name = 'inicio.html'
    model = Cliente

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        if query:
            return qs.filter(nombre=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Cliente'
        return context


def addCarritoCompras(request,carrito_id,producto_id):
    cantidad = request.POST.get('cantidad','')
    carrito = CarritoCompras.objects.get(pk=carrito_id)
    carrito.addProducto(producto_id,cantidad)
    return

def removeCarritoCompras(request, carrito_id,producto_id):
    template_name = 'carrito.html'
    carrito = CarritoCompras.objects.get(pk=carrito_id)
    carrito.removeProducto(producto_id)
    return redirect('/carrito/')

def registerusuario(request):
    return render(request, 'registrarusuario.html')

def Login(request):
    return render(request, 'registration/login.html')

def Registrarse(request):
    template_name = 'registration/registrar.html'
    success_url = 'registrar-usuario'
    if request.method == 'POST':
        form = UserCreationFormCustom(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(success_url)
    else:
        form = UserCreationFormCustom()
    return render(request, template_name, {'form': form})

class AgregarClienteView(CreateView):
    template_name = 'agregar.html'
    model = Cliente
    form_class = AgregarClienteForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Agregar Cliente'
        return context

class FacturacionView(CreateView):
    template_name = 'facturacion.html'
    model = Factura
    form_class = RegistrarFacturaForm
    success_url = reverse_lazy('home')

    def get_initial(self):
        initial = super(FacturacionView, self).get_initial()
        initial['id_factura'] = self.kwargs['pk']
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carrito'] = CarritoCompras.objects.get(pk=self.kwargs['pk'])
        context['menu_active'] = 'Facturar Productos'
        return context

class CotizacionView(CreateView):
    template_name = 'cotizacion.html'
    model = Factura
    fields = "__all___"
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Cotizar Productos'
        return context

class RegistrarVendedorView(CreateView):
    template_name = 'formulario.html'
    model = VendedorUsuario
    form_class = Empleados
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Registrar Vendedor'
        return context

class RegistrarAdminView(LoginRequiredMixin, CreateView):
    model = AdministradorUsuario
    template_name = 'formulario.html'
    success_url = reverse_lazy('home') 
    form_class = CreateAdminUsuarioForm

    def get_form_kwargs(self):
        kwargs = super(RegistrarAdminView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(RegistrarAdminView, self).get_context_data(**kwargs)
        context['menu_active'] = 'Registrar Administrador'
        return context

class CarritoComprasView(ListView):
    template_name = 'carrito.html'
    model = CarritoCompras

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        if query:
            return qs.filter(nombre=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda'
        context['carrito_id'] = 2
        return context

class AgregarProductosView(CreateView):
    template_name = 'agregar.html'
    model = Producto
    form_class = AgregarProductoForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Agregar Productos'
        return context

class AgregarDistribuidorView(CreateView):
    template_name = 'agregar.html'
    model = Distribuidor
    form_class = AgregarDistribuidorForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Agregar Distribuidor'
        return context

class ClienteListView(ListView):
    template_name = 'busqueda.html'
    model = Cliente
    paginate_by = 10  # if pagination is desired

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        qs = qs.filter(estado = 'A')
        if query:
            return qs.filter(nombre=query)
        return qs.order_by('-id')[:10:-1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Cliente'
        return context

class BusquedaProductos(ListView):
    template_name = 'busqueda_producto.html'
    model = Producto

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        if query:
            return qs.filter(nombre=query)
        return qs.order_by('-id')[:10:-1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda'
        context['carrito_id'] = 2
        return context

class GestionarProductos(ListView):
    template_name = 'gestionar_producto.html'
    model = Producto

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        if query:
            return qs.filter(nombre=query)

        return qs.order_by('-id')[:10:-1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda'
        context['carrito_id'] = 2
        return context

class DistribuidorListView(ListView):
    template_name = 'busqueda.html'
    model = Distribuidor
    paginate_by = 10  # if pagination is desired

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        qs = qs.filter(estado='A')
        if query:
            return qs.filter(nombre=query)
        return qs.order_by('-id')[:10:-1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Distribuidor'
        return context

class FacturaListView(ListView):
    template_name = 'busqueda.html'
    model = Factura
    paginate_by = 10  # if pagination is desired

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        if query:
            return qs.filter(nombre=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Factura'
        return context

class PedidoListView(ListView):
    template_name = 'busqueda.html'
    model = Pedido
    paginate_by = 10  # if pagination is desired

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        if query:
            return qs.filter(nombre=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Pedido'
        return context

class FacturasListView(ListView):
    template_name = 'busqueda.html'
    model = Distribuidor
    paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Distribuidor'
        return context

class UpdateCliente(UpdateView):
    template_name = 'update_cliente.html'
    fields = '__all__'
    model = Cliente
    success_url = reverse_lazy('home')

class UpdateDistribuidor(UpdateView):
    template_name = 'update_distribuidor.html'
    fields = '__all__'
    model = Distribuidor
    success_url = reverse_lazy('home')

class UpdateProducto(UpdateView):
    template_name = 'update_producto.html'
    fields = '__all__'
    model = Producto
    success_url = reverse_lazy('home')

def DeleteCliente(request, pk):
    Cliente.objects.filter(pk=pk).update(estado = 'I')

    return HttpResponseRedirect("/busqueda/cliente")

def DeleteDistribuidor(request, pk):
    Distribuidor.objects.filter(pk=pk).update(estado = 'I')

    return HttpResponseRedirect("/busqueda/distribuidor")