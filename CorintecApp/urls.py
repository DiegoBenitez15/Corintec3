from django.contrib import admin
from django.urls import path
from CorintecApp import views
from django.urls import include, path

urlpatterns = [
    path('',views.Login, name='login'),
    path('home/', views.home.as_view(), name='home'),
    path('registrarse/', views.Registrarse, name='registrar'),
    path('carrito/', views.CarritoComprasView.as_view(), name='carrito'),
    path('busqueda/producto', views.BusquedaProductos.as_view(), name='busqueda'),
    path('gestionar/producto', views.GestionarProductos.as_view(), name='gestionar-producto'),
    path('busqueda/cliente', views.ClienteListView.as_view(), name='busqueda-cliente'),
    path('busqueda/distribuidor', views.DistribuidorListView.as_view(), name='busqueda-distribuidor'),
    path('busqueda/pedido', views.PedidoListView.as_view(), name='busqueda-pedido'),
    path('busqueda/factura', views.FacturaListView.as_view(), name='busqueda-factura'),
    path('agregar/cliente', views.AgregarClienteView.as_view(), name='agregar-cliente'),
    path('agregar/distribuidor', views.AgregarDistribuidorView.as_view(), name='agregar-distribuidor'),
    path('agregar/producto', views.AgregarProductosView.as_view(), name='agregar-producto'),
    path('editar/cliente/<int:pk>', views.UpdateCliente.as_view(), name='editar-cliente'),
    path('editar/distribuidor/<int:pk>', views.UpdateDistribuidor.as_view(), name='editar-distribuidor'),
    path('editar/producto/<int:pk>', views.UpdateProducto.as_view(), name='editar-producto'),
    path('registrar/usuario', views.registerusuario, name='registrar-usuario'),
    path('eliminar/cliente/<int:pk>', views.DeleteCliente, name='eliminar-cliente'),
    path('eliminar/distribuidor/<int:pk>', views.DeleteDistribuidor, name='eliminar-distribuidor'),
    path('registrar/administrador', views.RegistrarAdminView.as_view(), name='registrar-administrador'),
    path('registrar/vendedor', views.RegistrarVendedorView.as_view(), name='registrar-vendedor'),
    path('add/carrito/<int:carrito_id>/producto/<int:producto_id>',views.addCarritoCompras, name='add-carrito'),
    path('remove/carrito/<int:carrito_id>/producto/<int:producto_id>',views.removeCarritoCompras, name='remove-carrito'),
    path('carrito/<int:carrito_id>/cliente/<int:cliente_id>/facturacion', views.FacturacionView.as_view(), name='facturar-producto'),
    path('carrito/cotizar', views.CotizacionView.as_view(), name='cotizar-producto'),
    path('carrito/<int:carrito_id>/buscar/cliente/', views.FiltrarCliente.as_view(), name='filtrar-cliente'),
    path('orden/compra/', views.OrdenCompraView.as_view(), name='orden-compra'),
]