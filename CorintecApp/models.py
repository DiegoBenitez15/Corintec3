from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=30)
    direccion = models.CharField(max_length=200)
    correo = models.CharField(max_length=30)
    telefono = models.CharField(max_length=14)

    def __str__(self):
        return self.nombre + ' ' + self.apellido

class Distribuidor(models.Model):
    nombre = models.CharField(max_length=30)
    correo = models.CharField(max_length=30)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=14)

class Cargo(models.Model):
    nombre = models.CharField(max_length=30,null=True)

class Empleados(models.Model):
    masculinos = 0
    femenino = 1
    otros = 2
    t_genero = ((masculinos, 'HOMBRE'), (femenino, 'MUJER'), (otros, 'OTROS'))
    nombre = models.CharField(max_length=30,null=True)
    apellido = models.CharField(max_length=30,null=True)
    correo = models.CharField(max_length=30,null=True)
    genero = models.PositiveIntegerField(choices=t_genero,null=True)
    telefono = models.CharField(max_length=14,null=True)
    cargo = models.ForeignKey(Cargo,on_delete=models.CASCADE,null=True)
    fecha_nacimiento = models.DateField(null=True)

    def __str__(self):
        return self.nombre + ' ' + self.apellido