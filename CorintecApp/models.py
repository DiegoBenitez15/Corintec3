from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
import random,string

t_genero = (('M', 'HOMBRE'), ('F', 'MUJER'), ('O', 'OTROS'))
t_eliminado = (('A', 'ACTIVO'), ('I', 'INACTIVO'))

def random_string():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_uppercase + string.digits) for _ in range(10))

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
    codigo = models.CharField(default=random_string,max_length=10)
    nombre = models.CharField(max_length=50)
    marca = models.CharField(max_length=120)
    descripcion = models.TextField(max_length=70)
    cantidad = models.IntegerField(default=0)
    precio_venta = models.FloatField(default=0)
    registrado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    ganancia = models.IntegerField(default=0)
    estado_producto = ((0, 'Sin Stock'), (1, 'Con Stock'))
    estado = models.IntegerField(choices=estado_producto, default=0)

    def update_estado(self):
        pass

    def producto_str(self):
        return [v[1] for v in self.estado_producto if v[0] == self.estado][0].title()

class Lista_Productos(models.Model):
    producto = models.ForeignKey(Producto,on_delete=models.CASCADE,null=True)
    cantidad = models.IntegerField(default=0)
    precio = models.FloatField(default=0)

class CarritoCompras(models.Model):
    producto_add = models.ManyToManyField(Lista_Productos)
    subtotal = models.FloatField(default=0)
    itbis = models.FloatField(default=0)
    total = models.FloatField(default=0)

    def actualizarPrecios(self):
        suma = 0
        for i in self.producto_add.all():
            suma += i.producto.precio_venta * i.cantidad
        self.subtotal = suma
        self.itbis = suma * 0.18
        self.total = self.subtotal + self.itbis
        self.save()

    def actualizarPrecios_ordenCompra(self):
        suma = 0
        for i in self.producto_add.all():
            suma += i.precio * i.cantidad
        self.subtotal = suma
        self.itbis = suma * 0.18
        self.total = self.subtotal + self.itbis
        self.save()

    def addProducto(self,producto_id,cantidad):
        for i in self.producto_add.all():
            if i.producto.pk == producto_id:
                c = self.producto_add.get(producto__id=producto_id)
                c.cantidad = int(cantidad)
                c.save()
                self.actualizarPrecios()
                return

        c =  Lista_Productos.objects.create(producto=Producto.objects.get(pk=producto_id),cantidad=cantidad)
        self.producto_add.add(c)
        self.actualizarPrecios()
        return

    def addProductoOrdenCompra(self,producto_id,cantidad,precio):
        for i in self.producto_add.all():
            if i.producto.pk == producto_id:
                c = self.producto_add.get(producto__id=producto_id)
                c.cantidad = int(cantidad)
                c.precio = precio
                c.save()
                self.actualizarPrecios_ordenCompra()
                return

        c = Lista_Productos.objects.create(producto=Producto.objects.get(pk=producto_id), cantidad=cantidad,precio=precio)
        self.producto_add.add(c)
        self.actualizarPrecios_ordenCompra()
        return

    def removeProductoOrdenCompra(self,producto_id):
        c = self.producto_add.get(producto_id=producto_id)
        self.producto_add.remove(c)
        c.delete()
        self.actualizarPrecios_ordenCompra()

    def cleanProductoOrdenCompra(self):
        productos = self.producto_add

        for i in self.producto_add.all():
            self.producto_add.remove(i)
            i.delete()

        self.actualizarPrecios_ordenCompra()

    def removeProducto(self,producto_id):
        c = self.producto_add.get(producto_id=producto_id)
        self.producto_add.remove(c)
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
    productos = models.ForeignKey(CarritoCompras, on_delete=models.CASCADE, null=True,related_name="productos")

    def __str__(self):
        return self.nombre + ' ' + self.apellido

class AdministradorUsuario(Empleados):
    usuario = models.OneToOneField(User,on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.usuario.roles.add(Role.ADMINISTRADOR)
        self.carrito = CarritoCompras.objects.create()
        self.productos = CarritoCompras.objects.create()
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

    def estado_str(self):
        return [v[1] for v in t_eliminado if v[0] == self.estado][0].title()

    def genero_str(self):
        return [v[1] for v in t_genero if v[0] == self.genero][0].title()

class Distribuidor(models.Model):
    nombre = models.CharField(max_length=30)
    correo = models.CharField(max_length=30)
    direccion = models.TextField(max_length=200)
    telefono = models.CharField(max_length=14)
    identificacion = models.CharField(max_length=30, null=True)
    estado = models.CharField(max_length=10, null=True, choices=t_eliminado, default="A")

    def __str__(self):
        return self.nombre

    def estado_str(self):
        return [v[1] for v in t_eliminado if v[0] == self.estado][0].title()

class RegistroCompras(models.Model):
    producto = models.ForeignKey(Producto,on_delete=models.CASCADE)
    distribuidor = models.ForeignKey(Distribuidor,on_delete=models.CASCADE)
    fecha_compra = models.DateField(auto_now_add=True, null=True)
    precio_compra = models.FloatField(default=0)
    cantidad = models.IntegerField(default=0)

Efectivo = 0
Credito = 1
Deposito = 2
t_pago = ((Efectivo, 'EFECTIVO'), (Credito, 'CREDITO'), (Deposito, 'DEPOSITO'))

class Factura(models.Model):
    codigo = models.CharField(default=random_string, max_length=10)
    fecha = models.DateField(auto_now_add=True,null=True)
    productos = models.ManyToManyField(Lista_Productos)
    totalPago = models.FloatField(null=True)
    subTotal = models.FloatField(null=True)
    ITBIS = models.FloatField(null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True)
    tipoPago = models.PositiveIntegerField(choices=t_pago,null=True)

    def t_pago_str(self):
        return [v[1] for v in t_pago if v[0] == self.tipoPago][0].title()


en_curso = 0
cancelado = 1
entregado = 2
t_estadoEnvio =((en_curso, 'En Curso'),(cancelado, 'Cancelado'), (entregado, 'Entregado'))
t_estadoOrdenCompra =((en_curso,'En Curso'),(cancelado, 'Cancelado'), (entregado, 'Entregado'))

class OrdenEnvio(models.Model):
    fecha_envio = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(User, on_delete=models.CASCADE,related_name='registrado_por')
    recibido_por = models.ForeignKey(User, on_delete=models.CASCADE,null=True,related_name='recibido_por')
    estadoEnvio = models.PositiveIntegerField(choices=t_estadoEnvio, null=True)

    def orden_envio_str(self):
        return [v[1] for v in t_estadoEnvio if v[0] == self.estadoEnvio][0].title()

class OrdenCompra(models.Model):
    codigo = models.CharField(default=random_string,max_length=10)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(null=True)
    productos = models.ManyToManyField(Lista_Productos)
    distribuidor = models.ForeignKey(Distribuidor, on_delete=models.CASCADE, null=True)
    estado = models.PositiveIntegerField(choices=t_estadoOrdenCompra, null=True)
    recibido_por = models.ForeignKey(User, on_delete=models.CASCADE, null=True,related_name='recibido')
    registrado_por = models.ForeignKey(User, on_delete=models.CASCADE, null=True,related_name='registrado')

    def orden_compra_str(self):
        return [v[1] for v in t_estadoOrdenCompra if v[0] == self.estado][0].title()

    def cambiar_estado(self,estado_acccion,user):
        if(estado_acccion == 'Terminado'):
            self.estado = 2
            self.registrado_por = User.objects.get(pk = user)
            self.fecha_entrega = datetime.now()
        elif (estado_acccion == 'Cancelado'):
            self.estado = 1
        self.save()
    
    def actualizarProductos(self,orden_id):
        orden = OrdenCompra.objects.get(pk=orden_id)
        for i in orden.productos.all():
            producto = Producto.objects.get(pk=i.producto.pk)
            producto.cantidad += i.cantidad
            producto.precio_venta = i.precio + (i.precio * (producto.ganancia / 100))
            producto.save()

class Pedido(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, null=True)
    orden_envio = models.ForeignKey(OrdenEnvio, on_delete=models.CASCADE, null=True)

    def cambiar_estado(self,estado_acccion,user):
        if(estado_acccion == 'Terminado'):
            self.orden_envio.estadoEnvio = 2
            self.orden_envio.recibido_por = User.objects.get(pk = user)
            self.orden_envio.fecha_entrega = datetime.now()
        elif (estado_acccion == 'Cancelado'):
            self.orden_envio.estadoEnvio = 1
            productos = self.factura.productos
            self.orden_envio.recibido_por = User.objects.get(pk=user)
            self.orden_envio.fecha_entrega = datetime.now()
            for i in productos.all():
                i.producto.cantidad = i.producto.cantidad + i.cantidad
                i.producto.save()

        self.orden_envio.save()
        self.factura.save()
        self.save()
