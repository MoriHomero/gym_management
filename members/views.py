# members/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Socio, Pago, IngresosMensuales
from .forms import SocioForm, PagoForm, ReportForm
from django.db.models import Sum
from django.utils import timezone
from django.shortcuts import render, redirect
from .models import Pago
from django.db.models import Sum
from datetime import timedelta
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count 
from django.http import JsonResponse
import csv
import datetime
from openpyxl import Workbook



def socio_list(request):
    query = request.GET.get('q')
    order_by = request.GET.get('order_by', 'nombre')
    socios = Socio.objects.all()
    
    if query:
        socios = socios.filter(
            Q(nombre__icontains=query) |
            Q(email__icontains=query) |
            Q(telefono__icontains=query) 
        )
    
    socios = socios.order_by(order_by)
    
    paginator = Paginator(socios, 10)  # Mostrar 10 socios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'order_by': order_by,
    }
    
    return render(request, 'members/socio_list.html', context)

def socio_detail(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    pagos = Pago.objects.filter(socio=socio).order_by('-fecha_pago')
    return render(request, 'members/socio_detail.html', {'socio': socio, 'pagos': pagos})



def socio_new(request):
    if request.method == 'POST':
        form = SocioForm(request.POST)
        if form.is_valid():
            socio = form.save(commit=False)
            primer_fecha_pago = form.cleaned_data['primer_fecha_pago']
            monto_ingresado = form.cleaned_data['monto']  # Obtener el monto ingresado del formulario
            try:
                monto = float(monto_ingresado) if monto_ingresado else 0.0
            except ValueError:
                monto = 0.0  # Default to 0.0 if conversion fails
            
            socio.save()
            
            # Crear el primer pago
            Pago.objects.create(socio=socio, fecha_pago=primer_fecha_pago, monto=monto, pagado=True)
            
            # Generar un pedido de pago para el mes siguiente
            proxima_fecha_pago = primer_fecha_pago + timezone.timedelta(days=30)
            Pago.objects.create(socio=socio, monto=monto, fecha_pago=proxima_fecha_pago)
            
            return redirect('socio_detail', pk=socio.pk)
    else:
        form = SocioForm()
    return render(request, 'members/crear_socio.html', {'form': form})

def socio_edit(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    if request.method == "POST":
        form = SocioForm(request.POST, instance=socio)
        if form.is_valid():
            socio = form.save()
            return redirect('socio_detail', pk=socio.pk)
    else:
        form = SocioForm(instance=socio)
    return render(request, 'members/socio_edit.html', {'form': form})

def socio_delete(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    
    # Verificar si hay pagos asociados al socio
    pagos_asociados = Pago.objects.filter(socio=socio).exists()
    
    if pagos_asociados:
        # Si hay pagos asociados, mostrar un mensaje de error o redirigir a alguna página
        return render(request, 'members/socio_delete_error.html', {'socio': socio})
    
    # Verificar si se está enviando el formulario de confirmación de eliminación
    if request.method == 'POST':
        # Si el formulario se envía con el método POST, eliminar el socio
        socio.delete()
        # Redirigir de vuelta a la lista de socios
        return redirect('socio_list')
    
    # Si la solicitud es GET y no hay pagos asociados, mostrar el formulario de confirmación de eliminación
    return render(request, 'members/socio_delete_confirmation.html', {'socio': socio})


def socio_delete_error(request):
    return render(request, 'members/socio_delete_error.html')

def pago_list(request):
    pagos = Pago.objects.all().order_by('-fecha_pago')  # Ordenar los pagos por fecha de pago de forma descendente

    # Filtrar los pagos por nombre
    search_query = request.GET.get('search')
    if search_query:
        pagos = pagos.filter(socio__nombre__icontains=search_query)

    paginator = Paginator(pagos, 10)  # Mostrar 10 pagos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'members/pago_list.html', {'page_obj': page_obj, 'search_query': search_query})

def pago_detail(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    return render(request, 'members/pago_detail.html', {'pago': pago})

def pago_new(request):
    if request.method == "POST":
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save()
            return redirect('pago_detail', pk=pago.pk)
    else:
        form = PagoForm()
    return render(request, 'members/pago_edit.html', {'form': form})

def pago_edit(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    if request.method == "POST":
        form = PagoForm(request.POST, instance=pago)
        if form.is_valid():
            form.save()
            return redirect('pago_detail', pk=pk)
    else:
        form = PagoForm(instance=pago)
    return render(request, 'members/pago_edit.html', {'form': form})

def pago_delete(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    
    if request.method == 'POST':
        # Verificar si el pago está marcado como pagado
        if pago.pagado:
            # Obtener la fecha del pago
            fecha_pago = pago.fecha_pago
            
            # Obtener los ingresos mensuales correspondientes al mes del pago
            ingresos_mensuales = IngresosMensuales.objects.filter(mes__year=fecha_pago.year, mes__month=fecha_pago.month).first()
            
            if ingresos_mensuales:
                # Restar el monto del pago de los ingresos mensuales
                ingresos_mensuales.ingresos -= pago.monto
                ingresos_mensuales.save()
        
        # Actualizar el informe de método de pago
        informe_mes = f"{pago.fecha_pago.year}-{pago.fecha_pago.month:02d}"  # Formato YYYY-MM
        informe = informe_metodo_pago(request)
        if informe_mes in informe:
            if pago.comentarios == 'Efectivo':
                informe[informe_mes]['Efectivo'] -= 1
            elif pago.comentarios == 'Transferencia':
                informe[informe_mes]['Transferencia'] -= 1
        
        # Eliminar el pago
        pago.delete()
        
        # Redirigir a la lista de pagos
        return redirect('pago_list')

    return render(request, 'members/pago_delete_confirmation.html', {'pago': pago})

def pago_delete_confirmation(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    return render(request, 'members/pago_delete_confirmation.html', {'pago': pago})

def informe_metodo_pago(request):
    # Obtener la cantidad de pagos por mes y método de pago
    pagos_por_mes = Pago.objects.values('fecha_pago__year', 'fecha_pago__month', 'comentarios').annotate(cantidad=Count('id'))
    
    # Estructurar los datos para el template
    informe = {}
    for pago in pagos_por_mes:
        mes = f"{pago['fecha_pago__year']}-{pago['fecha_pago__month']:02d}"  # Formato YYYY-MM
        if mes not in informe:
            informe[mes] = {'Efectivo': 0, 'Transferencia': 0}
        if pago['comentarios'] == 'Efectivo':
            informe[mes]['Efectivo'] += pago['cantidad']
        elif pago['comentarios'] == 'Transferencia':
            informe[mes]['Transferencia'] += pago['cantidad']
    
    return render(request, 'members/informe_metodo_pago.html', {'informe': informe})

def ingresos_mensuales(request):
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    current_month_end = (current_month_start + timezone.timedelta(days=32)).replace(day=1)
    
    ingresos = Pago.objects.filter(fecha_pago__gte=current_month_start, fecha_pago__lt=current_month_end, pagado=True).aggregate(Sum('monto'))
    return render(request, 'members/ingresos_mensuales.html', {'ingresos': ingresos['monto__sum']})

def pagos_atrasados(request):
    # Obtener parámetros de consulta
    nombre_query = request.GET.get('nombre')
    mes_query = request.GET.get('mes')
    order_by = request.GET.get('order_by', 'nombre')

    # Filtrar los pagos por nombre y mes si hay una consulta
    pagos = Pago.objects.all()
    if nombre_query:
        pagos = pagos.filter(socio__nombre__icontains=nombre_query)
    
    if mes_query:
        pagos = pagos.filter(fecha_pago__month=mes_query)

    # Obtener la fecha actual
    fecha_actual = timezone.now().date()

    # Filtrar los pagos que no están marcados como pagados y cuya fecha de pago sea menor o igual a la fecha actual
    pagos_atrasados = pagos.filter(pagado=False, fecha_pago__lt=fecha_actual)

    # Marcar socios cuya entrada no está permitida
    socios_no_permitidos = pagos_atrasados.values_list('socio_id', flat=True).distinct()
    Socio.objects.filter(id__in=socios_no_permitidos).update(entrada_permitida=False)

    # Permitir la entrada a los socios que ya no están en la lista de pagos atrasados
    socios_permitidos = Socio.objects.exclude(id__in=socios_no_permitidos)
    socios_permitidos.update(entrada_permitida=True)

    # Contexto para renderizar la plantilla
    context = {
        'pagos_atrasados': pagos_atrasados,
        'nombre_query': nombre_query,
        'mes_query': mes_query,
        'order_by': order_by,
    }

    return render(request, 'members/pagos_atrasados.html', context)


def marcar_pago_realizado(request, pago_id):
    pago = Pago.objects.get(id=pago_id)
    pago.pagado = True
    pago.save()
    
    # Genero fecha de cobro para el mes siguiente
    fecha_siguiente_pago = pago.fecha_pago + timezone.timedelta(days=30) #30 días
    Pago.objects.create(socio=pago.socio, monto=pago.monto, fecha_pago=fecha_siguiente_pago, fecha_vencimiento_siguiente_pago=fecha_siguiente_pago + timezone.timedelta(days=30))
    
    return redirect('pagos_atrasados')


def calcular_ingresos_mensuales():
    # Traigo los pagos que están marcados como pagados
    pagos_pagados = Pago.objects.filter(pagado=True)

    # Traigo todos los meses que contienen pagos
    meses_con_pagos = pagos_pagados.dates('fecha_pago', 'month', order='DESC')

    # Itero sobre cada mes que contiene pagos y calculo los ingresos
    for mes in meses_con_pagos:
        ingresos_mes = pagos_pagados.filter(fecha_pago__year=mes.year, fecha_pago__month=mes.month).aggregate(Sum('monto'))['monto__sum'] or 0
        
        # Muestro o creo el registro de ingresos mensuales para este mes
        ingresos_mensuales, created = IngresosMensuales.objects.get_or_create(mes=mes, defaults={'ingresos': ingresos_mes})

        if not created:
            ingresos_mensuales.ingresos = ingresos_mes
            ingresos_mensuales.save()

def ingresos_mensuales_view(request):
    calcular_ingresos_mensuales()
    ingresos = IngresosMensuales.objects.all()
    return render(request, 'members/ingresos_mensuales.html', {'ingresos': ingresos})

def verificar_estado_entrada(request, id_socio):
    if request.method == 'GET':
        try:
            socio = Socio.objects.get(id=id_socio)
            estado_entrada = socio.entrada_permitida
            return JsonResponse({'estado_entrada': estado_entrada})
        except Socio.DoesNotExist:
            return JsonResponse({'error': 'Socio no encontrado'}, status=404)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

#views

def generar_informe_excel(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            entidad = form.cleaned_data['entidad']
            entrada_permitida = form.cleaned_data.get('entrada_permitida')
            mes = form.cleaned_data.get('mes')

            if entidad == 'cliente':
                clientes = Socio.objects.filter(entrada_permitida=entrada_permitida)
                data = [(cliente.nombre, cliente.email) for cliente in clientes]
                headers = ['Nombre', 'Email']
            elif entidad == 'pago':
                pagos = Pago.objects.filter(pagado=False)
                if mes:
                    pagos = pagos.filter(fecha_pago__month=mes.month)
                data = [(pago.socio.nombre, pago.fecha_pago, pago.monto) for pago in pagos]
                headers = ['Nombre del Socio', 'Fecha de Pago', 'Monto']

            wb = Workbook()
            ws = wb.active
            ws.append(headers)
            for row in data:
                ws.append(row)

            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename=informe_{entidad}.xlsx'
            wb.save(response)
            return response
    else:
        form = ReportForm()

    return render(request, 'members/generar_informes.html', {'form': form})