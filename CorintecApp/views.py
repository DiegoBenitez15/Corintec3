from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import *
from .models import *
from .forms import *

# Create your views here.

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

def Login(request):
    return render(request, 'registration/login.html')

def Registrarse(request):
    data = {'form': CustomUserCreationForm}
    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            user = authenticate(username = formulario.cleaned_data["username"], password = formulario.cleaned_data["password1"])
            login(request,user)
            messages.success(request,'Te has registrado correctamente')
            return redirect(to = "login")
        data["form"] = formulario
    return render(request, 'registration/registrar.html',data)

class AgregarClienteView(CreateView):
    template_name = 'agregar.html'
    model = Cliente
    form_class = AgregarClienteForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Agregar Cliente'
        return context

class RegistrarVendedorView(CreateView):
    template_name = 'formulario.html'
    model = Empleados
    form_class = RegistrarForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Registrar Vendedor'
        return context

class RegistrarAdminView(CreateView):
    template_name = 'formulario.html'
    model = Empleados
    form_class = RegistrarForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Registrar Administrador'
        return context

class CarritoCompras(ListView):
    template_name = 'carrito.html'
    model = Producto

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        if query:
            return qs.filter(nombre=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda'
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
        qs = qs.filter(estado = 'A').order_by('-id')[:10:-1]
        if query:
            return qs.filter(nombre=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Cliente'
        return context

class BusquedaProductos(ListView):
    template_name = 'busqueda_producto.html'
    model = Producto

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs).order_by('-id')[:10:-1]
        query = self.request.GET.get('nombre_producto')
        if query:
            return qs.filter(nombre=query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda'
        return context

class DistribuidorListView(ListView):
    template_name = 'busqueda.html'
    model = Distribuidor
    paginate_by = 10  # if pagination is desired

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        qs = qs.filter(estado='A').order_by('-id')[:10:-1]
        if query:
            return qs.filter(nombre=query)
        return qs

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
    form_class = AgregarDistribuidorForm
    model = Distribuidor
    success_url = reverse_lazy('home')

def DeleteCliente(request, pk):
    Cliente.objects.filter(pk=pk).update(estado = 'I')

    return HttpResponseRedirect("/busqueda/cliente")