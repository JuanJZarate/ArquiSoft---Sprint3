from django.db import models

class Proyecto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()


    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    nombre = models.CharField(max_length=255)
    email = models.EmailField()
    proyecto = models.ForeignKey(Proyecto, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')

    def __str__(self):
        return self.nombre


class ConsumoMensual(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='consumos')
    mes = models.IntegerField()
    anio = models.IntegerField()
    costo_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.proyecto.nombre} - {self.mes}/{self.anio}: ${self.costo_total}"
