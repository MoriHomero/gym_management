# members/forms.py

from django import forms
from .models import Socio, Pago

class SocioForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = ['nombre', 'email', 'telefono', 'primer_fecha_pago', 'comentarios']

    monto = forms.DecimalField(label='Monto', required=False)

class PagoForm(forms.ModelForm):
    # Definir opciones para el campo comentarios
    FORMA_PAGO_CHOICES = [
        ('', 'Seleccione una opción'),  # Opción en blanco
        ('Efectivo', 'Efectivo'),
        ('Transferencia', 'Transferencia'),
    ]

    # Modificar el campo comentarios para usar opciones predefinidas
    comentarios = forms.ChoiceField(choices=FORMA_PAGO_CHOICES, required=False)

    class Meta:
        model = Pago
        fields = ['socio', 'fecha_pago', 'monto', 'pagado', 'comentarios']
        
class ReportForm(forms.Form):
    ENTIDAD_CHOICES = [
        ('cliente', 'Cliente'),
        ('pago', 'Pago'),
    ]
    entidad = forms.ChoiceField(choices=ENTIDAD_CHOICES)
    entrada_permitida = forms.BooleanField(required=False, label='Entrada permitida')
    mes = forms.DateField(widget=forms.SelectDateWidget, required=False)
    exportar = forms.BooleanField(required=False, initial=False, label='Exportar a Excel')