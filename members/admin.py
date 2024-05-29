# members/admin.py

from django.contrib import admin
from .models import Socio, Pago, IngresosMensuales

admin.site.register(Socio)
admin.site.register(Pago)
admin.site.register(IngresosMensuales)
