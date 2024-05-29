# members/models.py

from django.db import models
from django.utils import timezone
from datetime import timedelta

class Socio(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    fecha_registro = models.DateField(auto_now_add=True)
    primer_fecha_pago = models.DateField()
    telefono = models.CharField(max_length=15, blank=True, null=True)  # Campo opcional
    comentarios = models.TextField(blank=True, null=True)  # Nuevo campo de comentarios
    entrada_permitida = models.BooleanField(default=True)  # Campo para indicar si el socio puede entrar

    def __str__(self):
        return self.nombre

class Pago(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(default=timezone.now)
    pagado = models.BooleanField(default=False)
    fecha_vencimiento_siguiente_pago = models.DateField(null=True, blank=True)
    FORMAS_DE_PAGO = [
        ('EF', 'Efectivo'),
        ('TR', 'Transferencia'),
    ]
    comentarios = models.TextField(blank=True, null=True)  # Campo de comentarios



    def save(self, *args, **kwargs):
        if self.pk:  # Verificar si es un objeto existente
            # Guardo estado original del pago antes de la modificación
            original_pago = Pago.objects.get(pk=self.pk)
            # Llamar al método save original de py
            super().save(*args, **kwargs)
            # Verificar si se ha modificado el estado de "pagado"
            if original_pago.pagado != self.pagado and self.pagado:  # Si el pago se marco como pagado = True
                # Crear un nuevo pago con la fecha del mes siguiente
                proxima_fecha_pago = self.fecha_pago + timezone.timedelta(days=30)
                Pago.objects.create(socio=self.socio, fecha_pago=proxima_fecha_pago, monto=self.monto)
        else:  # Si es un nuevo objeto, llamar al método save original de py
            super().save(*args, **kwargs)

    def __str__(self):
        return f'Pago de {self.socio.nombre} en fecha {self.fecha_pago}'
    

class IngresosMensuales(models.Model):
    mes = models.DateField(unique=True)
    ingresos = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Ingresos de {self.mes.strftime("%B %Y")}: {self.ingresos}'