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
from django.http import JsonResponse
from fpdf import FPDF
from io import StringIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from html import escape
import io

# Create your views here.

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
def render_to_pdf(template_src, context_dict):
    if context_dict is None:
        context_dict = {}
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result,
                            encoding='UTF-8')
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
def GenerateCotizacionPdf(request,cliente_id,carrito_id):
    #Retrieve data or whatever you need
    carrito = CarritoCompras.objects.get(pk=carrito_id)
    cliente = Cliente.objects.get(pk=cliente_id)
    totales = []

    for i in carrito.producto_add.all():
        totales.append(i.cantidad * i.producto.precio_venta)

    context = {'pagesize':'A4','cliente':cliente,'carrito':carrito,'totales':totales}
    return render_to_pdf('cotizacion_pdf.html',context)

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
def GenerateFacturaPdf(request,factura_id):
    #Retrieve data or whatever you need
    factura = Factura.objects.get(pk=factura_id)
    context = {'pagesize':'A4','factura':factura}
    return render_to_pdf('factura_pdf.html',context)

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class home(ListView):
    template_name = 'inicio.html'
    model = Pedido
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(orden_envio__estadoEnvio=0)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Cliente'
        return context

@method_decorator([login_required, administador_required()], name='dispatch')
def addCarritoComprasOrdenCompra(request,carrito_id,producto_id):
    cantidad = request.POST.get('cantidad','')
    precio = request.POST.get('precio', '')
    carrito = CarritoCompras.objects.get(pk=carrito_id)
    carrito.addProductoOrdenCompra(producto_id,cantidad,precio)

@method_decorator([login_required, administador_required()], name='dispatch')
def removeCarritoComprasOrdenCompra(request, carrito_id,producto_id):
    carrito = CarritoCompras.objects.get(pk=carrito_id)
    carrito.removeProductoOrdenCompra(producto_id)

@method_decorator([login_required, administador_required()], name='dispatch')
def cleanCarritoComprasOrdenCompra(request,carrito_id):
    carrito = CarritoCompras.objects.get(pk=carrito_id)
    carrito.cleanProductoOrdenCompra()

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class addCarritoCompras(View):
    def post(self, request, carrito_id,producto_id):
        cantidad = request.POST.get('cantidad','')
        carrito = CarritoCompras.objects.get(pk=carrito_id)
        carrito.addProducto(producto_id,cantidad)
        return JsonResponse({})

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
def removeCarritoCompras(request, carrito_id,producto_id):
    carrito = CarritoCompras.objects.get(pk=carrito_id)
    carrito.removeProducto(producto_id)
    return redirect('/carrito/')

@method_decorator([login_required], name='dispatch')
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

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class AgregarClienteView(CreateView):
    template_name = 'agregar.html'
    model = Cliente
    form_class = AgregarClienteForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Agregar Cliente'
        return context

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class FacturacionView(CreateView):
    template_name = 'facturacion.html'
    model = Factura
    form_class = RegistrarFacturaForm
    success_url = reverse_lazy('home')

    def get_initial(self):
        initial = super(FacturacionView, self).get_initial()
        initial['carrito_id'] = self.kwargs['carrito_id']
        initial['cliente'] = self.kwargs['cliente_id']
        initial['user'] = self.request.user
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carrito'] = CarritoCompras.objects.get(pk=self.kwargs['carrito_id'])
        context['menu_active'] = 'Facturar Productos'
        return context

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class CotizacionView(CreateView):
    template_name = 'cotizacion.html'
    model = Factura
    fields = "__all___"
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Cotizar Productos'
        return context

@method_decorator([login_required], name='dispatch')
class RegistrarVendedorView(CreateView):
    model = AdministradorUsuario
    template_name = 'formulario.html'
    success_url = reverse_lazy('home')
    form_class = CreateVendedorUsuarioForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Registrar Vendedor'
        return context

    def get_form_kwargs(self):
        kwargs = super(RegistrarVendedorView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

@method_decorator([login_required], name='dispatch')
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

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class CarritoComprasView(ListView):
    template_name = 'carrito.html'
    model = CarritoCompras

    def get_queryset(self, *args, **kwargs):
        if self.request.user.get_roles() == 'administrador':
            qs = super().get_queryset(*args, **kwargs).filter(pk = self.request.user.administradorusuario.carrito_id)
        if self.request.user.get_roles() == 'vendedor':
            qs = super().get_queryset(*args, **kwargs).filter(pk=self.request.user.vendedorusuario.carrito_id)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda'
        if self.request.user.get_roles() == 'administrador':
            context['carrito_id'] = self.request.user.administradorusuario.carrito_id
        if self.request.user.get_roles() == 'vendedor':
            context['carrito_id'] = self.request.user.vendedorusuario.carrito_id
        return context

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class AgregarProductosView(CreateView):
    template_name = 'agregar.html'
    model = Producto
    form_class = AgregarProductoForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super(AgregarProductosView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Agregar Productos'
        return context

@method_decorator([login_required, administador_required()], name='dispatch')
class AgregarOrdenCompraView(CreateView):
    template_name = 'agregar.html'
    model = Producto
    form_class = AgregarProductoForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super(AgregarOrdenCompraView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Agregar Orden Compra'
        return context

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class AgregarDistribuidorView(CreateView):
    template_name = 'agregar.html'
    model = Distribuidor
    form_class = AgregarDistribuidorForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Agregar Distribuidor'
        return context

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class ClienteListView(ListView):
    template_name = 'busqueda.html'
    model = Cliente
    paginate_by = 10  # if pagination is desired

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        qs = qs.filter(estado = 'A')
        if query:
            if qs.filter(nombre__icontains=query):
                return qs.filter(nombre__icontains=query)
            elif qs.filter(identificacion=query):
                return qs.filter(identificacion=query)
            else:
                return []
        return qs.order_by('-id')[:10:-1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Cliente'
        return context

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class BusquedaProductos(ListView):
    template_name = 'busqueda_producto.html'
    model = Producto

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        if query:
            if qs.filter(nombre__icontains=query):
                return qs.filter(nombre__icontains=query)
            elif qs.filter(codigo=query):
                return qs.filter(codigo=query)
            else:
                return []
        return qs.order_by('-nombre')[:10:-1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda'
        if self.request.user.get_roles() == 'administrador':
            context['carrito_id'] = self.request.user.administradorusuario.carrito_id
        if self.request.user.get_roles() == 'vendedor':
            context['carrito_id'] = self.request.user.vendedorusuario.carrito_id

        return context

@method_decorator([login_required, administador_required()], name='dispatch')
class GestionarProductos(ListView):
    template_name = 'gestionar_producto.html'
    model = Producto

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        if query:
            if qs.filter(nombre__icontains=query):
                return qs.filter(nombre__icontains=query)
            elif qs.filter(codigo=query):
                return qs.filter(codigo=query)
            else:
                return []
        return qs.order_by('-nombre')[:10:-1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda'
        context['carrito_id'] = 2
        return context

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class DistribuidorListView(ListView):
    template_name = 'busqueda.html'
    model = Distribuidor
    paginate_by = 10  # if pagination is desired

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        qs = qs.filter(estado = 'A')
        if query:
            if qs.filter(nombre__icontains=query):
                return qs.filter(nombre__icontains=query)
            elif qs.filter(identificacion=query):
                return qs.filter(identificacion=query)
            else:
                return []
        return qs.order_by('-id')[:10:-1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Distribuidor'
        return context

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class FacturaListView(ListView):
    template_name = 'busqueda.html'
    model = Factura
    paginate_by = 10  # if pagination is desired

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs).order_by('-id')
        query = self.request.GET.get('nombre_producto')
        if query:
            if qs.filter(codigo=query):
                return qs.filter(codigo=query)
            else:
                return []
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Factura'
        return context

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class PedidoListView(ListView):
    template_name = 'busqueda.html'
    model = Pedido
    paginate_by = 10  # if pagination is desired

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs).order_by('-id')
        query = self.request.GET.get('nombre_producto')
        if query:
            if qs.filter(factura__codigo=query):
                return qs.filter(factura__codigo=query)
            else:
                return []
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Pedido'
        return context

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class FacturasListView(ListView):
    template_name = 'busqueda.html'
    model = Distribuidor
    paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Busqueda Distribuidor'
        return context

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class UpdateCliente(UpdateView):
    template_name = 'update_cliente.html'
    fields = '__all__'
    model = Cliente
    success_url = reverse_lazy('home')

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class UpdateDistribuidor(UpdateView):
    template_name = 'update_distribuidor.html'
    fields = '__all__'
    model = Distribuidor
    success_url = reverse_lazy('home')

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class UpdateProducto(UpdateView):
    template_name = 'update_producto.html'
    fields = ['nombre','marca','descripcion','ganancia']
    model = Producto
    success_url = reverse_lazy('gestionar-producto')

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
def DeleteCliente(request, pk):
    Cliente.objects.filter(pk=pk).update(estado = 'I')

    return HttpResponseRedirect("/busqueda/cliente")

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
def DeleteDistribuidor(request, pk):
    Distribuidor.objects.filter(pk=pk).update(estado = 'I')

    return HttpResponseRedirect("/busqueda/distribuidor")

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class FiltrarCliente(ListView):
    template_name = 'filtrar_clientes.html'
    model = Cliente
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        qs = qs.filter(estado='A')
        if query:
            if qs.filter(nombre__icontains=query):
                return qs.filter(nombre__icontains=query)
            elif qs.filter(identificacion=query):
                return qs.filter(identificacion=query)
            else:
                return []
        return qs.order_by('-id')[:10:-1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carrito_id'] = self.kwargs['carrito_id']
        context['menu_active'] = 'Filtrar Cliente'
        return context

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class FiltrarFactura(ListView):
    template_name = 'filtrar_factura.html'
    model = Factura
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs).order_by('-id')
        query = self.request.GET.get('nombre_producto')
        if query:
            if qs.filter(codigo=query):
                return qs.filter(codigo=query)
            else:
                return []
        return qs

    def get_context_data(self, **kwargs):
        id = []
        devoluciones = Devoluciones.objects.all()

        for i in devoluciones:
            id.append(i.factura.id)

        context = super().get_context_data(**kwargs)
        context['facturas'] = id
        context['menu_active'] = 'Filtrar Factura'
        return context

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class FiltrarClienteCotizacion(ListView):
    template_name = 'filtrar_clientes.html'
    model = Cliente
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        qs = qs.filter(estado='A')
        if query:
            if qs.filter(nombre__icontains=query):
                return qs.filter(nombre__icontains=query)
            elif qs.filter(identificacion=query):
                return qs.filter(identificacion=query)
            else:
                return []
        return qs.order_by('-id')[:10:-1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carrito_id'] = self.kwargs['carrito_id']
        context['menu_active'] = 'Filtrar Cliente Cotizacion'
        return context

@method_decorator([login_required, administador_required()], name='dispatch')
class OrdenCompraView(ListView):
    template_name = 'orden_compra.html'
    model = OrdenCompra
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs).order_by('estado')
        query = self.request.GET.get('nombre_producto')
        if query:
            return qs.filter(codigo=query)

        return qs

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class FiltrarDistribuidor(ListView):
    template_name = 'filtrar_distribuidor.html'
    model = Distribuidor
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        qs = qs.filter(estado='A')
        if query:
            if qs.filter(nombre__icontains=query):
                return qs.filter(nombre__icontains=query)
            elif qs.filter(identificacion=query):
                return qs.filter(identificacion=query)
            else:
                return []
        return qs.order_by('-id')[:10:-1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Filtrar Distribuidor'
        if self.request.user.get_roles() == 'administrador':
            context['carrito_id'] = self.request.user.administradorusuario.productos_id
        if self.request.user.get_roles() == 'vendedor':
            context['carrito_id'] = self.request.user.vendedorusuario.productos_id

        return context

@method_decorator([login_required, administador_required()], name='dispatch')
class FiltarProductos(ListView):
    template_name = 'filtrar_producto.html'
    model = Producto
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get('nombre_producto')
        if query:
            if qs.filter(nombre__icontains=query):
                return qs.filter(nombre__icontains=query)
            elif qs.filter(codigo=query):
                return qs.filter(codigo=query)
            else:
                return []
        return qs.order_by('-nombre')[:10:-1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Filtar Producto'
        if self.request.user.get_roles() == 'administrador':
            context['carrito_id'] = self.request.user.administradorusuario.productos_id
        if self.request.user.get_roles() == 'vendedor':
            context['carrito_id'] = self.request.user.vendedorusuario.productos_id
        context['distribuidor_id'] = self.kwargs['distribuidor_id']
        return context

@method_decorator([login_required, administador_required()], name='dispatch')
class OrdenEnvioFormularioView(CreateView):
    template_name = 'orden_compra_formulario.html'
    model = OrdenCompra
    form_class = RegistrarOrdenCompraForm
    success_url = reverse_lazy('home')

    def get_initial(self):
        initial = super(OrdenEnvioFormularioView, self).get_initial()
        initial['carrito_id'] = self.kwargs['carrito_id']
        initial['distribuidor'] = self.kwargs['distribuidor_id']
        initial['user'] = self.request.user
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['carrito'] = CarritoCompras.objects.get(pk=self.kwargs['carrito_id'])
        context['carrito_id'] = self.kwargs['carrito_id']
        context['carrito'] = CarritoCompras.objects.get(pk=self.kwargs['carrito_id'])
        context['menu_active'] = 'Facturar Productos'
        return context

@method_decorator([login_required, administador_required()], name='dispatch')
def CancelOrdenCompra(request, pk, user):
    orden = OrdenCompra.objects.get(pk=pk)
    orden.cambiar_estado('Cancelado',user)
    return HttpResponseRedirect("/ordencompra")

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
def TerminatePedido(request, pk, user):
    pedido = Pedido.objects.get(pk = pk)
    pedido.cambiar_estado('Terminado',user)
    return HttpResponseRedirect("/busqueda/pedido")

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
def CancelPedido(request, pk, user):
    pedido = Pedido.objects.get(pk=pk)
    pedido.cambiar_estado('Cancelado',user)
    return HttpResponseRedirect("/busqueda/pedido")

@method_decorator([login_required, administador_required()], name='dispatch')
def TerminateOrdenCompra(request, pk, user):
    orden = OrdenCompra.objects.get(pk = pk)
    orden.cambiar_estado('Terminado',user)
    orden.actualizarProductos(pk)
    return HttpResponseRedirect("/ordencompra")

@method_decorator([login_required], name='dispatch')
class ActualizarFiltroProducto(View):
    def get(self, request,carrito_id):
        carrito = CarritoCompras.objects.get(pk=carrito_id)
        id_productos = []
        cantidad = []

        for i in carrito.producto_add.all():
            id_productos.append(i.producto.pk)
            cantidad.append(i.cantidad)

        return JsonResponse({'id_productos': id_productos,'cantidad':cantidad})

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class chequearDisponibilidad(View):
    def post(self,request,producto_id):
        producto = Producto.objects.get(pk=producto_id)
        cantidad = request.POST.get('cantidad','')

        if(int(producto.cantidad) >= int(cantidad)):
            return JsonResponse({'respuesta':'si'})
        else:
            return JsonResponse({'respuesta':'no'})

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class VentasDashBoard(View):
    def post(self,request,t_venta):
        suma=0
        pedido = None
        if t_venta == 'Diario':
            pedido = Pedido.objects.filter(factura__fecha__day=timezone.now().day,orden_envio__estadoEnvio=2)
        elif t_venta == 'Mensual':
            pedido = Pedido.objects.filter(factura__fecha__month=timezone.now().month,orden_envio__estadoEnvio=2)
        elif t_venta == 'Anual':
            pedido = Pedido.objects.filter(factura__fecha__year=timezone.now().year,orden_envio__estadoEnvio=2)

        if pedido != None:
            for i in pedido.all():
                suma += i.factura.totalPago

        if t_venta == 'Total':
            suma = Factura.objects.filter(fecha__month=timezone.now().month).count()

        return JsonResponse({'suma':suma})


@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class ProductoAgotado(View):
    def post(self,request):
        return JsonResponse({'producto_agotado':Producto.objects.filter(cantidad=0).all().count()})

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
def InfoCliente(request,cliente_id):
    cliente = Cliente.objects.get(pk=cliente_id)
    return render(request, 'info_cliente.html',{'cliente':cliente})

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class DevolucionesListView(ListView):
    template_name = 'devoluciones.html'
    model = Devoluciones
    paginate_by = 10  # if pagination is desired

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs).order_by('-id')
        query = self.request.GET.get('nombre_producto')
        if query:
            if qs.filter(factura__codigo=query):
                return qs.filter(factura__codigo=query)
            else:
                return []
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Devoluciones'
        return context

@method_decorator([login_required, administador_or_vendedor_required()], name='dispatch')
class CreateDevoluciones(CreateView):
    template_name = 'create_devoluciones.html'
    model = Devoluciones
    form_class = CreateDevolucionesForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super(CreateDevoluciones, self).get_form_kwargs()
        kwargs['factura'] = Factura.objects.get(pk=self.kwargs['factura_id'])
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_active'] = 'Crear Devoluciones'
        return context