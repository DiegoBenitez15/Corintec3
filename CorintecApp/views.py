from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import *
from .models import *
from .forms import *

# Create your views here.

def home(request):
    return render(request, 'inicio.html')

def carrito(request):
    return render(request, 'carrito.html')

def busqueda(request):
    return render(request, 'busqueda_producto.html')

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Cliente'
        return context

    def get_queryset(self, *args, **kwargs):
        c = super(ClienteListView, self).get_queryset(*args, **kwargs)
        c = Cliente.objects.filter().all()
        return c


class DistribuidorListView(ListView):
    template_name = 'busqueda.html'
    model = Distribuidor
    paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Distribuidor'
        return context

class FacturasListView(ListView):
    template_name = 'busqueda.html'
    model = Distribuidor
    paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Distribuidor'
        return context

