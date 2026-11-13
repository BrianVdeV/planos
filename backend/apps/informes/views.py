"""Muestra las diferentes vistas de los informes de actividades."""
import os
from collections import defaultdict
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.db.models import Count, DurationField, ExpressionWrapper, F, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.table import Table, TableStyleInfo

from apps.expedientes.models import Expediente
from auth.models import Colaborador
from kanban.forms import ActividadForm
from kanban.models import Actividad


def resumen(request):
    """ Informes Resumen """
    return render(request, 'informes/resumen.html')


@login_required
def detallado(request):
    """ Informes Detallados """
    form = ActividadForm()
    context = {
        'form': form
    }
    return render(request, 'informes/detallado.html', context)


def promedio(request):
    """ Informes Promedio por Tarea """
    queryset = Actividad.objects.filter(
        fin__isnull=False,
        tarea__isnull=False,
        ot__isnull=False
    ).annotate(
        # 2. Calculamos la duración individual (evitando el nombre 'duracion' que da error)
        tiempo_calculado=ExpressionWrapper(
            F('fin') - F('inicio'),
            output_field=DurationField()
        )
    ).values(
        # 3. Agrupamos por Tarea
        'tarea__titulo'
    ).annotate(
        # 4. Sumamos todas las horas que esa tarea ha consumido en la historia
        suma_total_horas=Sum('tiempo_calculado'),

        # 5. Contamos en cuántas OTs ÚNICAS ha aparecido esa tarea
        cantidad_ots=Count('ot', distinct=True)
    ).order_by('tarea__titulo')
    # Construir lista de resultados para el template
    resultados = []

    for item in queryset:
        nombre = item.get('tarea__titulo')
        total_tiempo = item.get('suma_total_horas') or timedelta()
        num_ots = item.get('cantidad_ots') or 0

        if num_ots > 0 and total_tiempo:
            promedio_tiempo = total_tiempo / num_ots
            horas_decimales = promedio_tiempo.total_seconds() / 3600
        else:
            horas_decimales = 0.0

        resultados.append({
            'tarea': nombre,
            'promedio_horas': round(horas_decimales, 2),
            'num_ots': num_ots,
        })

    context = {
        'resultados': resultados
    }

    return render(request, 'informes/promedio.html', context)


@login_required
def informes_actividades(request):
    """ Vista de informes de actividades """
    form = ActividadForm()
    context = {
        'form': form
    }
    return render(request, 'informes/actividades.html', context)


def export_actividades_excel(request):
    """Genera y devuelve un archivo Excel con todas las actividades."""
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    search_value = request.GET.get('search_value', '').strip()

    # Filtrar actividades
    actividades = Actividad.objects.all().order_by('-id')
    if search_value:
        actividades = actividades.filter(
            Q(comentario__icontains=search_value) |
            Q(user__username__icontains=search_value) |
            Q(ot__nombre__icontains=search_value) |
            Q(ot__id__icontains=search_value)
        )

    if start_date and end_date:
        actividades = actividades.filter(
            inicio__date__range=(start_date, end_date)
        )

    # Crear el archivo Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Actividad"

    # Encabezados
    headers = [
        'ID OT', 'Nombre OT', 'Estado', 'Actividad', 'Descripción',
        'Nombre', 'Fecha', 'Total', 'Total Decimal'
    ]

    # Insertar encabezados en la primera fila
    ws.append(headers)

    # Insertar datos
    for actividad in actividades:
        expediente = Expediente.objects.filter(
            ot=actividad.ot).order_by('-id').first()

        ws.append([
            actividad.ot.id if actividad.ot else None,
            actividad.ot.nombre if actividad.ot else None,
            expediente.estado if expediente else None,
            actividad.tarea.titulo if actividad.tarea else None,
            actividad.comentario,
            actividad.user.username if actividad.user else None,
            actividad.inicio.strftime(
                '%d/%m/%Y') if actividad.inicio else None,
            actividad.total(),
            actividad.total_decimal()
        ])

    # Definir el rango de la tabla
    tabla_rango = f"A1:I{len(actividades) + 1}"
    tabla = Table(displayName="TablaActividad", ref=tabla_rango)

    # Aplicar estilo a la tabla
    estilo = TableStyleInfo(
        name="TableStyleLight9",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False
    )
    tabla.tableStyleInfo = estilo
    for row in range(1, ws.max_row + 1):  # Recorre todas las filas existentes
        ws.row_dimensions[row].height = 25

    # Agregar la tabla a la hoja de cálculo
    ws.add_table(tabla)

    # Ajustar el ancho de las columnas automáticamente
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Obtener la letra de la columna
        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except Exception:
                pass
        ws.column_dimensions[column].width = max_length + 2

    # Forzar que la columna de "Descripción" tenga un ancho de 50
    col_descripcion_index = headers.index(
        "Descripción") + 1  # Obtener el índice de la columna
    col_descripcion_letter = ws.cell(
        row=1, column=col_descripcion_index).column_letter
    ws.column_dimensions[col_descripcion_letter].width = 50
    # Determinar la última fila después de insertar los datos
    # +2 porque la primera fila es de encabezados
    ultima_fila = len(actividades) + 2

    # Agregar la fórmula en la columna "Total Decimal"
    col_total_decimal_index = headers.index(
        "Total Decimal") + 1  # Índice de la columna
    col_total_decimal_letter = ws.cell(
        row=1, column=col_total_decimal_index).column_letter

    # Escribir la fórmula en la última fila
    ws[f"{col_total_decimal_letter}{ultima_fila}"] = f"=SUBTOTALES(9, {col_total_decimal_letter}2:{col_total_decimal_letter}{ultima_fila-1})"
    # Configurar respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Informes_Detallado_' + \
        search_value+'_'+start_date+'_'+end_date+'.xlsx'

    wb.save(response)
    return response


def export_resumen_excel(request):
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    search_value = request.GET.get('search_value', '').strip()

    if not search_value:
        return JsonResponse({'error': 'El nombre del colaborador no puede estar vacío.'}, status=400)

    # 1. Obtener Datos
    actividades = Actividad.objects.all().order_by(
        'inicio')  # Ordenar por fecha para los gráficos
    user = User.objects.filter(username__icontains=search_value).first()

    colaborador = Colaborador.objects.filter(user=user).first()
    if colaborador:
        actividades = actividades.filter(user=user.id)
    else:
        return JsonResponse({'error': 'Colaborador no válido.'}, status=400)

    # Obtener el área del colaborador
    if colaborador and colaborador.area:
        nombre_area = colaborador.area.nombre.upper()
    else:
        nombre_area = 'GENERAL'

    if start_date and end_date:
        actividades = actividades.filter(
            inicio__date__range=(start_date, end_date))

    # --- Estructuras de Datos para la Tabla Principal ---
    actividades_dict = {}
    for actividad in actividades:
        if actividad.ot not in actividades_dict:
            actividades_dict[actividad.ot] = []
        actividades_dict[actividad.ot].append(actividad)

    # --- INICIO DE EXCEL ---
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte Semanal"

    # --- LÓGICA ORIGINAL DE TU TABLA (SIN CAMBIOS VISUALES) ---
    ws.merge_cells('A1:H1')
    title_cell = ws['A1']
    title_cell.value = f"REPORTE LABORAL SEMANAL DEL {start_date} AL {end_date} - DEL \nPERSONAL {search_value.upper()}  - ÁREA {nombre_area}"
    title_cell.font = Font(size=14, bold=True)
    title_cell.alignment = Alignment(
        horizontal='center', vertical='center', wrap_text=True)
    title_cell.fill = PatternFill(
        start_color="B0DD7F", end_color="B0DD7F", fill_type="solid")
    ws.row_dimensions[1].height = 50

    headers = ['OT', 'Nombre OT', 'Actividad', 'Responsable', 'Fechas de Elaboración',
               'Días Laborados conforme a lo delegado en sus funciones',
               'Cantidad de OT Trabajado (SEMANAL)', 'Horas SEMANAL Laborados Por OT']

    header_fill = PatternFill(start_color="C5D9F1",
                              end_color="C5D9F1", fill_type="solid")
    ws.append(headers)

    thin_border = Border(
        left=Side(style='thin', color='000000'),
        right=Side(style='thin', color='000000'),
        top=Side(style='thin', color='000000'),
        bottom=Side(style='thin', color='000000')
    )

    for cell in ws[2]:
        cell.alignment = Alignment(
            horizontal='center', vertical='center', wrap_text=True)
        cell.font = Font(bold=True)
        cell.fill = header_fill

    column_widths = {'A': 9, 'B': 25, 'C': 20,
                     'D': 13, 'E': 15, 'F': 10, 'G': 11, 'H': 15}
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    # Variables para recolectar datos para el GRÁFICO DE OTs (Pastel)
    data_grafico_ot = []  # Lista de tuplas (Nombre OT, Horas Decimales)

    for ot, actividades_ot in actividades_dict.items():
        actividades_texto = "\n".join(
            set(act.tarea.titulo for act in actividades_ot if act.tarea))
        fechas_texto = "\n".join(
            sorted(set(act.inicio.strftime('%d/%m/%Y') for act in actividades_ot)))
        dias_laborados = len(set(act.inicio.date() for act in actividades_ot))

        horas_totales = sum(
            (act.fin - act.inicio for act in actividades_ot if act.inicio and act.fin), timedelta())
        horas_totales_decimal = horas_totales.total_seconds() / \
            (24 * 3600)  # Formato Excel tiempo

        # Guardamos datos para grafico
        nombre_ot_str = ot.nombre if ot else "Sin OT"
        # Convertimos a horas enteras (float) para el gráfico, no fracción de día
        horas_para_grafico = horas_totales.total_seconds() / 3600
        data_grafico_ot.append([nombre_ot_str, round(horas_para_grafico, 2)])

        row = [
            ot.id if ot else None,
            ot.nombre if ot else None,
            actividades_texto,
            actividades_ot[0].user.username if actividades_ot and actividades_ot[0].user else None,
            fechas_texto,
            dias_laborados,
            1,
            horas_totales_decimal
        ]
        ws.append(row)
        for cell in ws[ws.max_row]:
            cell.alignment = Alignment(
                horizontal='center', vertical='center', wrap_text=True)

    # --- PIE DE PAGINA TABLA ORIGINAL ---
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        meses_es = {"January": "ENERO", "February": "FEBRERO", "March": "MARZO", "April": "ABRIL",
                    "May": "MAYO", "June": "JUNIO", "July": "JULIO", "August": "AGOSTO",
                    "September": "SEPTIEMBRE", "October": "OCTUBRE", "November": "NOVIEMBRE", "December": "DICIEMBRE"}
        dia_inicio = start_date_obj.strftime('%d')
        dia_fin = end_date_obj.strftime('%d')
        mes_nombre = meses_es[start_date_obj.strftime('%B')]
        mes_nombre1 = meses_es[end_date_obj.strftime('%B')]
        anio = start_date_obj.strftime('%Y')
    except:
        dia_inicio, dia_fin, mes_nombre, mes_nombre1, anio = "", "", "", "", ""

    total_row = ws.max_row + 1
    ws.merge_cells(start_row=total_row, start_column=1,
                   end_row=total_row, end_column=6)
    total_cell = ws.cell(row=total_row, column=1)
    total_cell.value = f"TOTAL DE OTS TRABAJADOS DEL {dia_inicio} {mes_nombre}  AL {dia_fin} {mes_nombre1} {anio}"
    total_cell.font = Font(size=12, bold=True)
    total_cell.alignment = Alignment(
        horizontal='center', vertical='center', wrap_text=True)

    columna_ot_trabajado = 7
    inicio_datos = 3
    fin_datos = total_row - 1
    if fin_datos < inicio_datos:
        fin_datos = inicio_datos  # Evitar error si no hay datos

    ws.cell(row=total_row,
            column=columna_ot_trabajado).value = f"=SUM(G{inicio_datos}:G{fin_datos})"
    ws.cell(row=total_row, column=columna_ot_trabajado).font = Font(
        size=12, bold=True)

    total_horas_row = total_row + 1
    ws.merge_cells(start_row=total_horas_row, start_column=1,
                   end_row=total_horas_row, end_column=7)
    ws.cell(row=total_horas_row,
            column=1).value = f"TOTAL HORAS ELABORACIÓN DE OTS DEL {dia_inicio} {mes_nombre} AL {dia_fin} {mes_nombre1} {anio}"
    ws.cell(row=total_horas_row, column=1).font = Font(size=12, bold=True)
    ws.cell(row=total_horas_row, column=1).alignment = Alignment(
        horizontal='center', vertical='center', wrap_text=True)

    ws.cell(row=total_horas_row,
            column=8).value = f"=SUM(H{inicio_datos}:H{fin_datos})"
    ws.cell(row=total_horas_row, column=8).font = Font(size=12, bold=True)

    for row in ws.iter_rows(min_col=8, max_col=8, min_row=3, max_row=ws.max_row):
        for cell in row:
            cell.number_format = "[hh]:mm:ss"

    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=8):
        for cell in row:
            cell.border = thin_border

    # =========================================================================
    # NUEVA SECCIÓN: GENERACIÓN DE GRÁFICOS (HOJA 2)
    # =========================================================================

    # Creamos una hoja nueva para mantener limpio el reporte original
    ws_graf = wb.create_sheet("Gráficos y Estadísticas")

    # 1. PREPARAR DATOS: HORAS POR DÍA (Gráfico de Barras)
    # Usamos un diccionario para sumar horas por fecha
    horas_por_dia = defaultdict(float)

    # Rellenar con 0 todos los días del rango para que el gráfico no tenga huecos feos
    try:
        delta = end_date_obj - start_date_obj
        for i in range(delta.days + 1):
            day = start_date_obj + timedelta(days=i)
            day_str = day.strftime('%d/%m')  # Formato DD/MM para el eje X
            horas_por_dia[day_str] = 0.0

        # Sumar horas reales
        for act in actividades:
            if act.inicio and act.fin:
                duracion = (act.fin - act.inicio).total_seconds() / 3600
                day_key = act.inicio.strftime('%d/%m')
                if day_key in horas_por_dia:
                    horas_por_dia[day_key] += duracion
    except:
        pass  # Si fallan las fechas, salta esta parte

    # --- ESCRIBIR DATOS DE BARRAS EN LA HOJA 2 ---
    ws_graf['A1'] = "Fecha"
    ws_graf['B1'] = "Horas Registradas"
    ws_graf['A1'].font = Font(bold=True)
    ws_graf['B1'].font = Font(bold=True)

    row_idx = 2
    for fecha, horas in horas_por_dia.items():
        ws_graf[f'A{row_idx}'] = fecha
        ws_graf[f'B{row_idx}'] = round(horas, 2)
        row_idx += 1

    last_row_barras = row_idx - 1

    # --- CREAR GRÁFICO DE BARRAS ---
    bar_chart = BarChart()
    bar_chart.type = "col"
    bar_chart.style = 10
    bar_chart.title = "Horas Trabajadas por Día"
    bar_chart.y_axis.title = 'Horas'
    bar_chart.x_axis.title = 'Día'

    # Definir datos y categorías
    data = Reference(ws_graf, min_col=2, min_row=1, max_row=last_row_barras)
    cats = Reference(ws_graf, min_col=1, min_row=2, max_row=last_row_barras)
    bar_chart.add_data(data, titles_from_data=True)
    bar_chart.set_categories(cats)
    bar_chart.shape = 4

    # Posicionar gráfico en la hoja
    ws_graf.add_chart(bar_chart, "D2")

    # --- 2. PREPARAR DATOS: HORAS POR OT (Gráfico de Pastel) ---
    # Ya recolectamos esto arriba en `data_grafico_ot`

    ws_graf['A20'] = "Proyecto (OT)"
    ws_graf['B20'] = "Total Horas"
    ws_graf['A20'].font = Font(bold=True)
    ws_graf['B20'].font = Font(bold=True)

    row_idx = 21
    for item in data_grafico_ot:
        ws_graf[f'A{row_idx}'] = item[0]  # Nombre OT
        ws_graf[f'B{row_idx}'] = item[1]  # Horas
        row_idx += 1

    last_row_pie = row_idx - 1

    if data_grafico_ot:  # Solo crear si hay datos
        pie = PieChart()
        pie.title = "Distribución de Tiempo por Proyecto"
        labels = Reference(ws_graf, min_col=1, min_row=21,
                           max_row=last_row_pie)
        data_pie = Reference(ws_graf, min_col=2,
                             min_row=20, max_row=last_row_pie)
        pie.add_data(data_pie, titles_from_data=True)
        pie.set_categories(labels)

        # Posicionar gráfico
        ws_graf.add_chart(pie, "D20")

    # Finalizar Response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"Reporte_Laboral_{start_date}_al_{end_date}_{search_value.upper()}_{nombre_area}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response

# Función auxiliar para que xhtml2pdf encuentre los archivos estáticos (Logo)


def link_callback(uri, rel):
    """
    Convierte un URI de HTML (ej. /static/img/logo.png) a una ruta de sistema de archivos.
    """
    # Maneja la URL estática de Django
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT,
                            uri.replace(settings.STATIC_URL, ""))
        if not os.path.isfile(path):
            result = finders.find(uri.replace(settings.STATIC_URL, ""))
            if result:
                if not isinstance(result, (list, tuple)):
                    path = result
                else:
                    path = result[0]
                return path
            return uri
        return path

    # Maneja rutas relativas
    elif uri.startswith("/"):
        path = os.path.join(settings.BASE_DIR, uri.lstrip('/'))
        if os.path.isfile(path):
            return path

    return uri
