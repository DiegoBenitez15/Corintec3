from django.contrib import admin
from django.urls import path
from CorintecApp import views
from django.urls import include, path

urlpatterns = [
    path('',views.Login, name='login'),
    path('home/', views.home.as_view(), name='home'),
    path('registrarse/', views.Registrarse, name='registrar'),
    path('carrito/', views.CarritoCompras.as_view(), name='carrito'),
    path('busqueda/producto', views.BusquedaProductos.as_view(), name='busqueda'),
    path('busqueda/cliente', views.ClienteListView.as_view(), name='busqueda-cliente'),
    path('busqueda/distribuidor', views.DistribuidorListView.as_view(), name='busqueda-distribuidor'),
    path('busqueda/pedido', views.PedidoListView.as_view(), name='busqueda-pedido'),
    path('busqueda/factura', views.FacturaListView.as_view(), name='busqueda-factura'),
    path('agregar/cliente', views.AgregarClienteView.as_view(), name='agregar-cliente'),
    path('agregar/distribuidor', views.AgregarDistribuidorView.as_view(), name='agregar-distribuidor'),
    path('agregar/producto', views.AgregarProductosView.as_view(), name='agregar-producto'),
    path('editar/cliente/<int:pk>', views.UpdateCliente.as_view(), name='editar-cliente'),
    path('editar/distribuidor/<int:pk>', views.UpdateDistribuidor.as_view(), name='editar-distribuidor'),
    path('registrar/usuario', views.registerusuario, name='registrar-usuario'),
    path('eliminar/cliente/<int:pk>', views.DeleteCliente, name='eliminar-cliente'),
    path('registrar/administrador', views.RegistrarAdminView.as_view(), name='registrar-administrador'),
    path('registrar/vendedor', views.RegistrarVendedorView.as_view(), name='registrar-vendedor'),
]