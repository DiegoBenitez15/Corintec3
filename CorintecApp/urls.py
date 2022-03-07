from django.contrib import admin
from django.urls import path
from CorintecApp import views
from django.urls import include, path

urlpatterns = [
    path('',views.Login, name='login'),
    path('home/', views.home, name='home'),
    path('registrarse/', views.Registrarse, name='registrar'),
    path('carrito/', views.CarritoCompras.as_view(), name='carrito'),
    path('busqueda/producto', views.BusquedaProductos.as_view(), name='busqueda'),
    path('busqueda/cliente', views.ClienteListView.as_view(), name='busqueda-cliente'),
    path('busqueda/distribuidor', views.DistribuidorListView.as_view(), name='busqueda-distribuidor'),
    path('agregar/cliente', views.AgregarClienteView.as_view(), name='agregar-cliente'),
    path('agregar/distribuidor', views.AgregarDistribuidorView.as_view(), name='agregar-distribuidor'),
    path('agregar/producto', views.AgregarProductosView.as_view(), name='agregar-producto'),
    path('editar/cliente/<int:pk>', views.UpdateCliente.as_view(), name='editar-cliente'),
]