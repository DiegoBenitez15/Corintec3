from django.db import models
from django.contrib.auth.models import AbstractUser

t_genero = (('M', 'HOMBRE'), ('F', 'MUJER'), ('O', 'OTROS'))

class Role(models.Model):
    VENDEDOR = 1
    ADMINISTRADOR = 2
    ROLE_CHOICES = (
        (VENDEDOR, 'paciente'),
        (ADMINISTRADOR, 'medico'),
    )
    id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, primary_key=True)

class User(AbstractUser):
    roles = models.ManyToManyField(Role)
    pass

class Cargo(models.Model):
    nombre = models.CharField(max_length=30,null=True)

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    marca = models.CharField(max_length=120)
    descripcion = models.TextField(max_length=70)
    cantidad = models.IntegerField(default=0)

class CarritoCompras(models.Model):
    productos = models.ManyToManyField(Producto)
    subtotal = models.FloatField(default=0)
    itbis = models.FloatField(default=0)
    total = models.FloatField(default=0)

class Empleados(models.Model):
    nombre = models.CharField(max_length=30,null=True)
    apellido = models.CharField(max_length=30,null=True)
    correo = models.CharField(max_length=30,null=True)
    genero = models.CharField(max_length=1,choices=t_genero,null=True)
    telefono = models.CharField(max_length=14,null=True)
    cargo = models.ForeignKey(Cargo,on_delete=models.CASCADE,null=True)
    fecha_nacimiento = models.DateField(null=True)
    identificacion = models.CharField(max_length=30, null=True)
    carrito = models.ForeignKey(CarritoCompras,on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre + ' ' + self.apellido

    def save(self, *args, **kwargs):
        paciente = super(Paciente, self)
        self.carrito = CarritoCompras.objects.create()
        paciente.save(*args, **kwargs)

class AdministradorUsuario(Empleados):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.usuario.roles.add(Role.ADMINISTRADOR)
        super(Paciente, self).save(*args, **kwargs)

class VendedorUsuario(Empleados):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.usuario.roles.add(Role.VENDEDOR)
        super(Paciente, self).save(*args, **kwargs)

class Cliente(models.Model):
    nombre = models.CharField(max_length=30,null=True)
    apellido = models.CharField(max_length=30,null=True)
    genero = models.CharField(max_length=1,choices=t_genero,null=True)
    direccion = models.TextField(max_length=200,null=True)
    correo = models.CharField(max_length=30,null=True)
    telefono = models.CharField(max_length=14,null=True)
    rnc = models.CharField(max_length=30,null=True)
    identificacion = models.CharField(max_length=30,null=True)

    def __str__(self):
        return self.nombre + ' ' + self.apellido

class Distribuidor(models.Model):
    nombre = models.CharField(max_length=30)
    correo = models.CharField(max_length=30)
    direccion = models.TextField(max_length=200)
    telefono = models.CharField(max_length=14)
    identificacion = models.CharField(max_length=30, null=True)

class RegistroCompras(models.Model):
    producto = models.ForeignKey(Producto,on_delete=models.CASCADE)
    distribuidor = models.ForeignKey(Distribuidor,on_delete=models.CASCADE)
    fecha_compra = models.DateField(auto_now_add=True, null=True)
    precio_compra = models.FloatField(null=True)
    cantidad = models.IntegerField(default=0)

class Pedido(models.Model):
    fecha = models.DateTimeField
    cliente = models.ForeignKey(Cliente,on_delete=models.CASCADE,null=True)

activo= 1
inactivo = 0
t_estadoEnvio =((activo, 'Activo'), (inactivo, 'Inactivo'))

class OrdenEnvio(models.Model):
    fecha_envio = models.DateTimeField
    empleado = models.ForeignKey(Empleados,on_delete=models.CASCADE,null=True)
    contactoEmpresa = models.CharField(max_length=50)
    pedido = models.ForeignKey(Pedido,on_delete=models.CASCADE,null=True)
    estadoEnvio = models.PositiveIntegerField(choices=t_estadoEnvio, null=True)

    def orden_evio_str(self):
        return [v[1] for v in self.t_estadoEnvio if v[0] == self.estadoEnvio][0].title()

Efectivo = 0
Credito = 1
Deposito = 2
t_pago = ((Efectivo, 'EFECTIVO'), (Credito, 'CREDITO'), (Deposito, 'DEPOSITO'))

class Factura(models.Model):
    fecha = models.DateField
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True)
    cantidad = models.PositiveIntegerField
    totalPago = models.FloatField
    subTotal = models.FloatField
    ITBIS = models.FloatField
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True)
    tipoPago = models.PositiveIntegerField(choices=t_pago,null=True)
    cliente = models.ForeignKey(Pedido, on_delete=models.CASCADE, null=True)

    def factura_str(self):
        return [v[1] for v in self.t_pago if v[0] == self.tipoPago][0].title()

