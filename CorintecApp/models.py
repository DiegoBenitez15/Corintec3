from django.db import models

t_genero = (('M', 'HOMBRE'), ('F', 'MUJER'), ('O', 'OTROS'))

class Cliente(models.Model):
    nombre = models.CharField(max_length=30,null=True)
    apellido = models.CharField(max_length=30,null=True)
    genero = models.CharField(max_length=1,choices=t_genero,null=True)
    direccion = models.TextField(max_length=200,null=True)
    correo = models.CharField(max_length=30,null=True)
    telefono = models.CharField(max_length=14,null=True)

    def __str__(self):
        return self.nombre + ' ' + self.apellido

class Distribuidor(models.Model):
    nombre = models.CharField(max_length=30)
    correo = models.CharField(max_length=30)
    direccion = models.TextField(max_length=200)
    telefono = models.CharField(max_length=14)

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

    def __str__(self):
        return self.nombre + ' ' + self.apellido

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(max_length=70)
    tipo = models.CharField(max_length=30)
    fecha_compra = models.DateField(auto_now_add=True,null=True)
    fecha_venta = models.DateField(null=True)
    precio_compra = models.FloatField(null=True)
    precio_venta = models.FloatField(null=True)
    distribuidor = models.ForeignKey(Distribuidor,on_delete=models.CASCADE,null=True)

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
