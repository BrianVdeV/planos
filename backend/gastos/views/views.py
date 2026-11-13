"""Vista para la app gastos"""
import json
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from gastos.models import CajaChica, Gasto, ReporteGasto, Saldo
from intranet.models import Ot


class GastosView(LoginRequiredMixin, View):
    """Vista para la app gastos"""

    def get(self, request):
        usuario = request.user
        resultado = Saldo.objects.filter(usuario=usuario).aggregate(
            total_saldo=Sum('saldo_actual'))
        saldo_usuario = resultado['total_saldo'] if resultado['total_saldo'] is not None else Decimal(
            '0.00')
        context = {
            "saldo_usuario": saldo_usuario
        }
        return render(request, 'gastos.html', context)


def crear_gastos(request):
    hoy = date.today().strftime("%Y-%m-%d")
    usuario = request.user  # 📌 Definir usuario antes de usarlo

    # Obtener la suma de todos los 'saldo_actual' para el usuario
    resultado = Saldo.objects.filter(usuario=usuario).aggregate(
        total_saldo=Sum('saldo_actual'))

    # Si no hay saldo, asigna un valor por defecto de Decimal('0.00')
    saldo_usuario = resultado['total_saldo'] if resultado['total_saldo'] is not None else Decimal(
        '0.00')
    ots = Ot.objects.filter(estado='Activo')
    gastos = Gasto.objects.all()
    context = {
        'ots': ots,
        'gastos': gastos,
        'filas': range(8),  # Genera 8 filas estáticas
        'hoy': hoy,
        "saldo_usuario": saldo_usuario
    }
    return render(request, 'gasto_add.html', context)


@login_required
def guardar_gasto(request):
    if request.method == "POST":

        usuario = request.user
        fecha_general = request.POST.get(
            "fechaGeneral", datetime.today().date())
        saldo_disponible = request.POST.get(
            "saldoInicial", "").strip()  # 🔹 Asegurar que no sea None
        total_monto_str = request.POST.get("totalMonto", "").strip()
        diferencia_monto_str = request.POST.get("diferenciaMonto", "").strip()

        # Convertir valores a Decimal solo si son válidos
        try:
            saldo_disponible = Decimal(
                saldo_disponible) if saldo_disponible else Decimal("0.00")
            total_monto = Decimal(
                total_monto_str) if total_monto_str else Decimal("0.00")
            diferencia_monto = Decimal(
                diferencia_monto_str) if diferencia_monto_str else Decimal("0.00")
        except InvalidOperation:
            return JsonResponse({"error": "Uno de los montos ingresados no es válido."}, status=400)

        # Obtener los saldos asociados al usuario y sumarlos
        saldos = Saldo.objects.filter(usuario=usuario)

        if saldos.exists():
            # Si existen varios saldos, sumamos los valores de saldo_actual
            saldo_total = sum(saldo.saldo_actual for saldo in saldos)
        else:
            # Si no existen saldos, asignamos un saldo por defecto
            saldo_total = Decimal("0.00")

        # Verificar que haya suficiente saldo
        if saldo_total >= total_monto:
            # Restar el monto gastado
            monto_temp = total_monto
            for saldo in saldos:
                if saldo.saldo_actual >= monto_temp:
                    saldo.saldo_actual -= monto_temp
                    saldo.save()
                    break
                else:
                    monto_temp -= saldo.saldo_actual
                    saldo.saldo_actual = Decimal("0.00")
                    saldo.save()

        # Crear el reporte de gasto
        reporte = ReporteGasto.objects.create(
            usuario=usuario,
            fecha=fecha_general,
            monto_recibido=saldo_disponible,
            total=total_monto,
            vuelto=diferencia_monto,
            estado_aprobacion=0,
            mensaje=""
        )

        # --- SECCIÓN MODIFICADA PARA ARCHIVOS ---
        # Capturamos la lista de archivos
        archivos_list = request.FILES.getlist("fileArchivo[]")

        # Guardar cada gasto de manera independiente
        ot_list = request.POST.getlist("sltOT[]")
        descripcion_list = request.POST.getlist("txtDescripcion[]")
        categoria_list = request.POST.getlist("sltCategoria[]")
        monto_list = request.POST.getlist("txtMonto[]")

        for i in range(len(descripcion_list)):
            # Validar que la descripción no esté vacía
            if descripcion_list[i].strip():

                # Intentamos obtener el archivo correspondiente al índice actual
                archivo_gasto = None
                if i < len(archivos_list):
                    archivo_gasto = archivos_list[i]

                Gasto.objects.create(
                    ot_id=ot_list[i] if ot_list[i] else None,
                    descripcion=descripcion_list[i],
                    categoria=categoria_list[i],
                    monto=Decimal(monto_list[i]) if monto_list[i] else 0,
                    reporte=reporte,  # Asignar el reporte creado
                    archivo=archivo_gasto  # Guardar la imagen
                )

        messages.success(request, "Gastos guardados exitosamente.")
        return redirect("gastos")

    return render(request, "gastos")


def editar_gastos(request, reporte_id):
    """Template para editar gastos"""
    reporte = get_object_or_404(ReporteGasto, id=reporte_id)
    gastos = Gasto.objects.filter(reporte_id=reporte_id)
    ots = Ot.objects.all()
    context = {
        'gastos': gastos,
        'reporte': reporte,
        'ots': ots,
    }
    return render(request, 'gasto_edit.html', context)


@login_required  # Asegura que el usuario esté autenticado
def actualizar_gasto(request):
    id_reporte = request.POST.get('id_reporte')

    if request.method == 'POST':
        gasto_ids = request.POST.getlist("gasto_id[]")
        eliminar_fila = request.POST.getlist("eliminar_fila[]")
        descripciones = request.POST.getlist('txtDescripcion[]')
        categorias = request.POST.getlist('sltCategoria[]')
        montos = request.POST.getlist('txtMonto[]')
        ots = request.POST.getlist('sltOT[]')

        usuario = request.user  # Obtener usuario autenticado

        num_items = max(len(descripciones), len(gasto_ids),
                        len(categorias), len(montos), len(ots))

        gasto_ids += [""] * (num_items - len(gasto_ids))
        eliminar_fila += ["0"] * (num_items - len(eliminar_fila))
        descripciones += [""] * (num_items - len(descripciones))
        categorias += [""] * (num_items - len(categorias))
        montos += ["0"] * (num_items - len(montos))
        ots += [""] * (num_items - len(ots))

        for i in range(num_items):
            if eliminar_fila[i] == "1" and gasto_ids[i]:
                Gasto.objects.filter(id=gasto_ids[i]).delete()

        for i in range(num_items):
            if eliminar_fila[i] == "1":
                continue

            gasto_id = gasto_ids[i]
            descripcion = descripciones[i]
            categoria = categorias[i]
            monto = float(montos[i]) if montos[i] else 0
            ot_id = ots[i].strip() if ots[i] else None

            if gasto_id:
                gasto = get_object_or_404(Gasto, id=gasto_id)
            else:
                gasto = Gasto(reporte_id=id_reporte)

            gasto.descripcion = descripcion
            gasto.categoria = categoria
            gasto.monto = monto
            gasto.fecha_creacion = request.POST.get('fechaGeneral')

            if ot_id:
                try:
                    gasto.ot = Ot.objects.get(id=ot_id)
                except Ot.DoesNotExist:
                    return JsonResponse({'error': f'La OT con ID {ot_id} no existe.'}, status=400)
            gasto.save()

        reporte = get_object_or_404(ReporteGasto, id=id_reporte)
        if reporte:
            reporte.monto_recibido = float(
                request.POST.get('montoRecibido', 0))
            reporte.total = float(request.POST.get('totalMonto', 0))
            reporte.vuelto = float(request.POST.get('diferenciaMonto', 0))
            reporte.fecha = request.POST.get('fechaGeneral')
            reporte.save()

        return redirect('aprobaciones')

    return redirect('aprobaciones')


def informes_gastos(request):
    """ Informes de Gastos"""
    ots = Ot.objects.all()
    usuarios = User.objects.filter(is_active=True)
    context = {
        'ots': ots,
        'usuarios': usuarios,
    }
    return render(request, 'informes.html', context)


def aprobaciones(request):
    """ Muestra los gastos organizados por estado de aprobación """

    if not request.user.is_superuser:

        return redirect("gastos")

    saldos = Saldo.objects.all()  # Obtener todos los saldos
    usuarios = User.objects.filter(is_active=True)  # Obtener usuarios activos

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "aprobar_todos":
            # Obtener todos los reportes pendientes
            reportes_pendientes = ReporteGasto.objects.filter(
                estado_aprobacion=1)

            for reporte in reportes_pendientes:
                # Eliminar SOLO el saldo del usuario correspondiente al reporte
                Saldo.objects.filter(usuario=reporte.usuario).delete()

            # Aprobar todos los reportes
            reportes_pendientes.update(estado_aprobacion=2)
            return redirect("aprobaciones")

        gasto_id = request.POST.get("gasto_id")
        reporte = get_object_or_404(ReporteGasto, id=gasto_id)

        if accion == "aprobar":
            reporte.estado_aprobacion = 2

            # Eliminar SOLO el saldo del usuario de este reporte
            Saldo.objects.filter(usuario=reporte.usuario).delete()

        elif accion == "rechazar":
            reporte.estado_aprobacion = 3
        else:
            return redirect("aprobaciones")

        reporte.save()
        return redirect("aprobaciones")

    # Obtener reportes de gasto según su estado de aprobación
    pendientes = ReporteGasto.objects.filter(
        estado_aprobacion=1).select_related("usuario")
    cajachica = ReporteGasto.objects.filter(
        estado_aprobacion=2).select_related("usuario")

    # Aquí calculamos el saldo para cada reporte de gasto, basándonos en el saldo inicial
    caja_chica_reportes = []
    for reporte in cajachica:
        # Obtener el saldo inicial para cada usuario desde CajaChica
        caja_chica_usuario = CajaChica.objects.filter(
            fecha=reporte.fecha).first()

        if caja_chica_usuario:
            saldo_restante = caja_chica_usuario.saldo_inicial + caja_chica_usuario.ingreso

            # Obtener todos los reportes de gasto para este usuario en la misma fecha
            reportes_gasto_usuario = ReporteGasto.objects.filter(
                fecha=reporte.fecha, usuario=reporte.usuario)

            # Restamos el monto de cada reporte de gasto al saldo restante
            for gasto in reportes_gasto_usuario:
                saldo_restante -= gasto.total

            # Guardamos los datos con el saldo calculado
            caja_chica_reportes.append({
                'fecha': reporte.fecha,
                'usuario': reporte.usuario.username,
                'total': reporte.total,
                'saldo': saldo_restante
            })

    context = {
        'pendientes': pendientes,
        'cajachica': cajachica,
        'saldos': saldos,  # Agregar saldos al contexto
        'usuarios': usuarios,
        'caja_chica_reportes': caja_chica_reportes,
    }

    return render(request, "aprobaciones.html", context)


def registrar_caja_chica(request):
    if request.method == 'POST':
        try:
            # Obtener la fecha seleccionada
            fecha_str = request.POST.get('fecha')
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()

            # Buscar si ya existe una Caja Chica en la fecha seleccionada
            caja_existente = CajaChica.objects.filter(fecha=fecha).first()

            # Si ya existe una Caja Chica, solo sumamos el nuevo ingreso
            if caja_existente:
                ingreso = request.POST.get('ingreso')

                # Validar que el ingreso sea numérico
                try:
                    ingreso = Decimal(ingreso)
                except InvalidOperation:
                    messages.error(
                        request, "El valor del ingreso debe ser numérico.")
                    return redirect('registrar_caja_chica')

                # Sumar el nuevo ingreso al existente
                caja_existente.ingreso += ingreso
                caja_existente.save()

                messages.success(request, "Ingreso actualizado correctamente.")
                return redirect('aprobaciones')

            # Si no existe Caja Chica en la fecha seleccionada, creamos una nueva
            else:
                # Obtener la última caja chica registrada
                ultima_caja = CajaChica.objects.all().order_by('-fecha').first()

                if ultima_caja:
                    # Tomar el saldo total de la última caja chica registrada
                    saldo_inicial = ultima_caja.total
                else:
                    # Pedir el saldo inicial si no hay día anterior
                    saldo_inicial = request.POST.get('saldo_inicial')

                ingreso = request.POST.get('ingreso')

                # Validar que los valores sean numéricos
                try:
                    saldo_inicial = Decimal(saldo_inicial)
                    ingreso = Decimal(ingreso)
                except InvalidOperation:
                    messages.error(
                        request, "Los valores de saldo inicial e ingreso deben ser numéricos.")
                    return redirect('registrar_caja_chica')

                # Crear y guardar la nueva Caja Chica
                caja_chica = CajaChica(
                    fecha=fecha, saldo_inicial=saldo_inicial, ingreso=ingreso)
                caja_chica.save()

                messages.success(
                    request, "Caja Chica registrada correctamente.")

        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")

        return redirect('aprobaciones')

    # Si no es un POST, solo redirige
    return redirect('aprobaciones')


def verificar_caja_chica(request):
    """
    Verifica si ya existe una Caja Chica en la fecha proporcionada
    y si existe una Caja Chica en la última fecha registrada.
    """
    fecha_str = request.GET.get('fecha')

    if not fecha_str:
        return JsonResponse({'error': 'Fecha no proporcionada'}, status=400)

    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)

    # Verificar si ya existe una Caja Chica en la fecha seleccionada
    existe_actual = CajaChica.objects.filter(fecha=fecha).exists()

    # Obtener la última fecha registrada de una Caja Chica
    ultima_fecha = CajaChica.objects.all().order_by('-fecha').first()
    if ultima_fecha:
        fecha_anterior = ultima_fecha.fecha
    else:
        fecha_anterior = None

    # Verificar si existe una Caja Chica en la fecha anterior
    if fecha_anterior:
        existe_anterior = CajaChica.objects.filter(
            fecha=fecha_anterior).exists()
    else:
        existe_anterior = False

    return JsonResponse({
        'existe_actual': existe_actual,  # Indica si hay una caja en la fecha seleccionada
        # Indica si hay una caja en la última fecha registrada
        'existe_anterior': existe_anterior
    })


@csrf_exempt  # Deshabilita CSRF solo si es necesario
def editar_caja_chica(request):
    if request.method == "POST":
        try:
            # Obtener los datos en formato JSON
            data = json.loads(request.body)

            caja_id = data.get("id")  # ID de la caja chica
            nuevo_ingreso = data.get("ingreso")  # Nuevo ingreso

            # Validar que el ingreso no sea None o inválido
            if nuevo_ingreso is None:
                return JsonResponse({"success": False, "message": "El ingreso no puede estar vacío."})

            # Buscar el registro en la base de datos
            caja_chica = CajaChica.objects.get(id=caja_id)

            # Convertir el ingreso a Decimal
            caja_chica.ingreso = Decimal(
                str(nuevo_ingreso))  # ✅ Conversión segura

            caja_chica.save()  # Guardar cambios

            return JsonResponse({"success": True, "message": "Ingreso actualizado correctamente."})
        except CajaChica.DoesNotExist:
            return JsonResponse({"success": False, "message": "Caja Chica no encontrada."})
        except ValueError:
            return JsonResponse({"success": False, "message": "Formato de ingreso inválido."})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error: {str(e)}"})

    return JsonResponse({"success": False, "message": "Método no permitido."}, status=405)
