from django.contrib import admin
from .models import Gasto, Saldo, ReporteGasto, CajaChica

# Register your models here.
admin.site.register(Gasto)
admin.site.register(Saldo)
admin.site.register(ReporteGasto)
admin.site.register(CajaChica)
