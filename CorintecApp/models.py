from django.db import models

t_genero = (('M', 'HOMBRE'), ('F', 'MUJER'), ('O', 'OTROS'))
t_eliminado = (('A', 'ACTIVO'), ('I', 'INACTIVO'))

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

class Cargo(models.Model):
    nombre = models.CharField(max_length=30,null=True)

class Empleados(models.Model):
    nombre = models.CharField(max_length=30,null=True)
    apellido = models.CharField(max_length=30,null=True)
    correo = models.CharField(max_length=30,null=True)
    genero = models.CharField(max_length=1,choices=t_genero,null=True)
    telefono = models.CharField(max_length=14,null=True)
    cargo = models.ForeignKey(Cargo,on_delete=models.CASCADE,null=True)
    fecha_nacimiento = models.DateField(null=True)
    identificacion = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.nombre + ' ' + self.apellido

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    marca = models.CharField(max_length=120)
    descripcion = models.TextField(max_length=70)
    cantidad = models.IntegerField(default=0)

class RegistroCompras(models.Model):
    producto = models.ForeignKey(Producto,on_delete=models.CASCADE)
    distribuidor = models.ForeignKey(Distribuidor,on_delete=models.CASCADE)
    fecha_compra = models.DateField(auto_now_add=True, null=True)
    precio_compra = models.FloatField(null=True)
    cantidad = models.IntegerField(default=0)

Efectivo = 0
Credito = 1
Deposito = 2
t_pago = ((Efectivo, 'EFECTIVO'), (Credito, 'CREDITO'), (Deposito, 'DEPOSITO'))

class Factura(models.Model):
    fecha = models.DateField(auto_now_add=True,null=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True)
    cantidad = models.PositiveIntegerField(default=0)
    totalPago = models.FloatField(null=True)
    subTotal = models.FloatField(null=True)
    ITBIS = models.FloatField(null=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True)
    tipoPago = models.PositiveIntegerField(choices=t_pago,null=True)


    def factura_str(self):
        return [v[1] for v in self.t_pago if v[0] == self.tipoPago][0].title()

activo= 1
inactivo = 0
t_estadoEnvio =((activo, 'Activo'), (inactivo, 'Inactivo'))

class OrdenEnvio(models.Model):
    fecha_envio = models.DateTimeField(null=True)
    empleado = models.ForeignKey(Empleados,on_delete=models.CASCADE,null=True)
    estadoEnvio = models.PositiveIntegerField(choices=t_estadoEnvio, null=True)

    def orden_evio_str(self):
        return [v[1] for v in self.t_estadoEnvio if v[0] == self.estadoEnvio][0].title()


class Pedido(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, null=True)
    orden_envio = models.ForeignKey(OrdenEnvio, on_delete=models.CASCADE, null=True)
