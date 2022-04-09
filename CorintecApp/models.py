from django.db import models
from django.contrib.auth.models import AbstractUser

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

class CarritoProductos(models.Model):
    producto = models.ForeignKey(Producto,on_delete=models.CASCADE,null=True)
    cantidad = models.IntegerField(default=0)

class CarritoCompras(models.Model):
    carrito_productos = models.ManyToManyField(CarritoProductos,null=True)
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
                c = CarritoProductos.objects.get(producto__id=producto_id)
                c.cantidad = c.cantidad + int(cantidad)
                c.save()
                self.actualizarPrecios()
                return


        c = CarritoProductos.objects.create(producto=Producto.objects.get(pk=producto_id),cantidad=cantidad)
        self.carrito_productos.add(c)
        self.actualizarPrecios()
        return

    def removeProducto(self,producto_id):
        c = CarritoProductos.objects.get(producto=producto_id)
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
    carrito = models.ForeignKey(CarritoCompras,on_delete=models.CASCADE,null=True)

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
    productos = models.ManyToManyField(CarritoProductos,null=True)
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
t_estadoEnvio =((en_curso, 'En Curso'),(pendiente, 'Pendiente'),(cancelado, 'Cancelado'), (finalizado, 'Finalizado'))

class OrdenEnvio(models.Model):
    fecha_envio = models.DateTimeField(auto_now_add=True)
    empleado = models.ForeignKey(Empleados,on_delete=models.CASCADE,null=True)
    estadoEnvio = models.PositiveIntegerField(choices=t_estadoEnvio, null=True)

    def orden_envio_str(self):
        return [v[1] for v in self.t_estadoEnvio if v[0] == self.estadoEnvio][0].title()

class Pedido(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, null=True)
    orden_envio = models.ForeignKey(OrdenEnvio, on_delete=models.CASCADE, null=True)