from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
import random

t_genero = (('M', 'HOMBRE'), ('F', 'MUJER'), ('O', 'OTROS'))
t_eliminado = (('A', 'ACTIVO'), ('I', 'INACTIVO'))

class Role(models.Model):
    VENDEDOR = 1
    ADMINISTRADOR = 2
    ROLE_CHOICES = (
        (VENDEDOR, 'vendedor'),
        (ADMINISTRADOR, 'administrador'),
    )
    id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)

    def __str__(self):
      return self.get_id_display()

class User(AbstractUser):
    roles = models.ManyToManyField(Role)

    def get_roles(self):
        s = ""
        for r in self.roles.all():
            s += str(r) + ","
        if len(s) > 0:
            s = s[:-1]
        return s

    def is_admin(self):
        return self.roles.filter(pk=Role.ADMINISTRADOR).exists()

    def is_vendedor(self):
        return self.roles.filter(pk=Role.VENDEDOR).exists()

class Cargo(models.Model):
    nombre = models.CharField(max_length=30,null=True)

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    marca = models.CharField(max_length=120)
    descripcion = models.TextField(max_length=70)
    cantidad = models.IntegerField(default=0)
    precio_venta = models.IntegerField(default=0)
    registrado_por = models.ForeignKey(User, on_delete=models.CASCADE)


class GrupoProductos(models.Model):
    producto = models.ForeignKey(Producto,on_delete=models.CASCADE,null=True)
    cantidad = models.IntegerField(default=0)

class GrupoProductosOrdenCompra(models.Model):
    producto = models.ForeignKey(Producto,on_delete=models.CASCADE,null=True)
    cantidad = models.IntegerField(default=0)
    precio_compra = models.FloatField(default=0)

class CarritoOrdenCompra(models.Model):
    carrito_productos = models.ManyToManyField(GrupoProductosOrdenCompra,null=True)

    def addProductoOrdenCompra(self, producto_id, cantidad, precio_compra):
        for i in self.carrito_productos.all():
            if i.producto.pk == producto_id:
                c = GrupoProductosOrdenCompra.objects.get(producto__id=producto_id)
                c.cantidad = c.cantidad + int(cantidad)
                c.precio_compra = precio_compra
                c.save()
                return

        c = GrupoProductosOrdenCompra.objects.create(producto=Producto.objects.get(pk=producto_id), cantidad=cantidad, precio_compra=precio_compra)
        self.carrito_productos.add(c)
        return

class CarritoCompras(models.Model):
    carrito_productos = models.ManyToManyField(GrupoProductos,null=True)
    subtotal = models.FloatField(default=0)
    itbis = models.FloatField(default=0)
    total = models.FloatField(default=0)

    def actualizarPrecios(self):
        suma = 0
        for i in self.carrito_productos.all():
            suma+= i.producto.precio_venta * i.cantidad
        self.subtotal = suma
        self.itbis = suma * 0.18
        self.total = self.subtotal + self.itbis
        self.save()

    def addProducto(self,producto_id,cantidad):
        for i in self.carrito_productos.all():
            if i.producto.pk == producto_id:
                c = GrupoProductos.objects.get(producto__id=producto_id)
                c.cantidad = c.cantidad + int(cantidad)
                c.save()
                self.actualizarPrecios()
                return


        c = GrupoProductos.objects.create(producto=Producto.objects.get(pk=producto_id),cantidad=cantidad)
        self.carrito_productos.add(c)
        self.actualizarPrecios()
        return

    def removeProducto(self,producto_id):
        c = GrupoProductos.objects.get(producto=producto_id)
        self.carrito_productos.remove(c)
        c.delete()
        self.actualizarPrecios()

class Empleados(models.Model):
    nombre = models.CharField(max_length=30,null=True)
    apellido = models.CharField(max_length=30,null=True)
    identificacion = models.CharField(max_length=30, null=True)
    correo = models.CharField(max_length=30,null=True)
    genero = models.CharField(max_length=1,choices=t_genero,null=True)
    telefono = models.CharField(max_length=14,null=True)
    fecha_nacimiento = models.DateField(null=True)
    carrito = models.ForeignKey(CarritoCompras,on_delete=models.CASCADE,null=True,related_name="carrito")
    productos = models.ForeignKey(CarritoOrdenCompra, on_delete=models.CASCADE, null=True,related_name="productos")

    def __str__(self):
        return self.nombre + ' ' + self.apellido

class AdministradorUsuario(Empleados):
    usuario = models.OneToOneField(User,on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.usuario.roles.add(Role.ADMINISTRADOR)
        self.carrito = CarritoCompras.objects.create()
        super(Empleados, self).save(*args, **kwargs)

class VendedorUsuario(Empleados):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.usuario.roles.add(Role.VENDEDOR)
        self.carrito = CarritoCompras.objects.create()
        super(Empleados, self).save(*args, **kwargs)

class Cliente(models.Model):
    nombre = models.CharField(max_length=30, null=True)
    apellido = models.CharField(max_length=30, null=True)
    genero = models.CharField(max_length=1, choices=t_genero, null=True)
    direccion = models.TextField(max_length=200, null=True)
    correo = models.CharField(max_length=30, null=True)
    telefono = models.CharField(max_length=14, null=True)
    rnc = models.CharField(max_length=30, null=True)
    identificacion = models.CharField(max_length=30, null=True)
    estado = models.CharField(max_length=10, null=True, choices=t_eliminado, default="A")

    def __str__(self):
        return self.nombre + ' ' + self.apellido

class Distribuidor(models.Model):
    nombre = models.CharField(max_length=30)
    correo = models.CharField(max_length=30)
    direccion = models.TextField(max_length=200)
    telefono = models.CharField(max_length=14)
    identificacion = models.CharField(max_length=30, null=True)
    estado = models.CharField(max_length=10, null=True, choices=t_eliminado, default="A")

class RegistroCompras(models.Model):
    producto = models.ForeignKey(Producto,on_delete=models.CASCADE)
    distribuidor = models.ForeignKey(Distribuidor,on_delete=models.CASCADE)
    fecha_compra = models.DateField(auto_now_add=True, null=True)
    precio_compra = models.FloatField(default=0,null=True)
    cantidad = models.IntegerField(default=0)

Efectivo = 0
Credito = 1
Deposito = 2
t_pago = ((Efectivo, 'EFECTIVO'), (Credito, 'CREDITO'), (Deposito, 'DEPOSITO'))

class Factura(models.Model):
    fecha = models.DateField(auto_now_add=True,null=True)
    productos = models.ManyToManyField(GrupoProductos,null=True)
    totalPago = models.FloatField(null=True)
    subTotal = models.FloatField(null=True)
    ITBIS = models.FloatField(null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True)
    tipoPago = models.PositiveIntegerField(choices=t_pago,null=True)

    def factura_str(self):
        return [v[1] for v in self.t_pago if v[0] == self.tipoPago][0].title()

en_curso = 0
pendiente = 1
cancelado = 2
finalizado = 3
entregado = 4
t_estadoEnvio =((en_curso, 'En Curso'),(pendiente, 'Pendiente'),(cancelado, 'Cancelado'), (finalizado, 'Finalizado'))
t_estadoOrdenCompra =((pendiente,'Pendiente'),(cancelado, 'Cancelado'), (entregado, 'Entregado'))

class OrdenEnvio(models.Model):
    fecha_envio = models.DateTimeField(auto_now_add=True)
    empleado = models.ForeignKey(Empleados,on_delete=models.CASCADE,null=True)
    estadoEnvio = models.PositiveIntegerField(choices=t_estadoEnvio, null=True)

    def orden_envio_str(self):
        return [v[1] for v in self.t_estadoEnvio if v[0] == self.estadoEnvio][0].title()

def random_string():
    return str(random.randint(1000000000, 9999999999))

class OrdenCompra(models.Model):
    codigo = models.CharField(default=random_string,primary_key=True,max_length=10)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(null=True)
    productos = models.ManyToManyField(GrupoProductos, null=True)
    distribuidor = models.ForeignKey(Distribuidor, on_delete=models.CASCADE, null=True)
    estado = models.PositiveIntegerField(choices=t_estadoOrdenCompra, null=True)
    recibido_por = models.ForeignKey(User, on_delete=models.CASCADE, null=True,related_name='recibido')
    registrado_por = models.ForeignKey(User, on_delete=models.CASCADE, null=True,related_name='registrado')

    def orden_compra_str(self):
        return [v[1] for v in t_estadoOrdenCompra if v[0] == self.estado][0].title()

    def cambiar_estado(self,estado_acccion,user):
        if(estado_acccion == 'Terminado'):
            self.estado = 4
            self.registrado_por = User.objects.get(pk = user)
            self.fecha_entrega = datetime.now()
        elif (estado_acccion == 'Cancelado'):
            self.estado = 2

        self.save()

class Pedido(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, null=True)
    orden_envio = models.ForeignKey(OrdenEnvio, on_delete=models.CASCADE, null=True)