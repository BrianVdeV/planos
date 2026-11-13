"""Vista de informes"""
import json
from io import BytesIO

from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side


def exportar_cajachica_excel(request):
    if request.method == "POST":
        data = json.loads(request.body)

        wb = Workbook()
        ws = wb.active
        ws.title = "Cajas Chicas"

        # Anchos de columna
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 13
        ws.column_dimensions['C'].width = 9
        ws.column_dimensions['D'].width = 10

        # Estilos
        encabezado_fill = PatternFill(
            start_color="313A46", end_color="313A46", fill_type="solid")
        gris_fill = PatternFill(start_color="D6DCE4",
                                end_color="D6DCE4", fill_type="solid")
        white_font = Font(color="FFFFFF", bold=True)
        bold_font = Font(bold=True)
        border_style = Border(
            left=Side(style='thin', color='000000'),
            right=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000')
        )

        # Encabezados
        headers = ["Fecha", "Usuario", "Total", "Saldo"]
        ws.append(headers)
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = encabezado_fill
            cell.font = white_font
            cell.border = border_style
            cell.alignment = Alignment(horizontal='center', vertical='center')

        row_num = 2

        for item in data:
            tipo = item.get("tipo")

            if tipo == "group-header" and item.get("label") == "Saldo Anterior":
                ws.merge_cells(start_row=row_num, start_column=1,
                               end_row=row_num, end_column=3)
                for col in range(1, 4):
                    cell = ws.cell(row=row_num, column=col)
                    if col == 1:
                        cell.value = "Saldo Anterior"
                    cell.fill = gris_fill
                    cell.font = bold_font
                    cell.border = border_style

                cell4 = ws.cell(row=row_num, column=4)
                cell4.value = float(item.get("total", 0))
                cell4.number_format = "0.00"
                cell4.fill = gris_fill
                cell4.font = bold_font
                cell4.border = border_style
                row_num += 1

            elif tipo == "data":
                ws.cell(row=row_num, column=1, value=item.get("fecha"))
                ws.cell(row=row_num, column=2, value=item.get("usuario_str"))

                valor_total_raw = item.get("total", None)
                if valor_total_raw in ("", None, 0, "0", 0.0):
                    total_cell = ws.cell(row=row_num, column=3, value="")
                else:
                    valor_total = float(valor_total_raw)
                    total_cell = ws.cell(
                        row=row_num, column=3, value=valor_total)
                    total_cell.number_format = "0.00"

                valor_saldo_raw = item.get("saldo", None)
                if valor_saldo_raw in ("", None, 0, "0", 0.0):
                    saldo_cell = ws.cell(row=row_num, column=4, value="")
                else:
                    valor_saldo = float(valor_saldo_raw)
                    saldo_cell = ws.cell(
                        row=row_num, column=4, value=valor_saldo)
                    saldo_cell.number_format = "0.00"

                # Bordes para fila
                for col in range(1, 5):
                    ws.cell(row=row_num, column=col).border = border_style

                row_num += 1

            elif tipo == "group-footer":
                label = item.get("label", "")
                if label in ["Saldo", "Totales"] or "Ingreso" in label:
                    ws.merge_cells(start_row=row_num, start_column=1,
                                   end_row=row_num, end_column=3)
                    for col in range(1, 4):
                        cell = ws.cell(row=row_num, column=col)
                        if col == 1:
                            cell.value = label  # ya definido arriba
                        cell.fill = gris_fill
                        cell.font = bold_font
                        cell.border = border_style

                    cell4 = ws.cell(row=row_num, column=4)
                    if "Ingreso" in label:
                        cell4.value = float(item.get("ingreso", 0))
                    else:
                        cell4.value = float(item.get("total", 0))
                    cell4.number_format = "0.00"
                    cell4.fill = gris_fill
                    cell4.font = bold_font
                    cell4.border = border_style
                    row_num += 1

        # Aplicar bordes a todos los encabezados
        for col in range(1, 5):
            ws.cell(row=1, column=col).border = border_style

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="cajas_chicas.xlsx"'
        return response

    return HttpResponse(status=405)
