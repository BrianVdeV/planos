$("#table").on("click", ".text-body", function () {
  currentTaskId = $(this).closest("tr").attr("id");
  $("#form-editar-tarea").attr("data-task-id", currentTaskId);
  $.get(`../../api/tarea/${currentTaskId}/`, function (data) {
    $('#offcanvas input[name="titulo"]').val(data.titulo);
    $('#offcanvas textarea[name="descripcion"]').val(data.descripcion);
    $('#offcanvas select[name="responsables"]').val(data.responsables);
    $('#offcanvas select[name="prioridad"]').val(data.prioridad);
    $('#offcanvas input[id="creacion"]').val(moment(data.creado).format("YYYY-MM-DD"));
    var fpVencimiento = $('#offcanvas input[name="vencimiento"]')[0]._flatpickr;
    if (fpVencimiento) {
      fpVencimiento.setDate(data.vencimiento || null);
    } else {
      if (data.vencimiento) {
        const fechaFormateada = moment(data.vencimiento).format("YYYY-MM-DD");
        $('#offcanvas input[name="vencimiento"]').val(fechaFormateada);
      } else {
        $('#offcanvas input[name="vencimiento"]').val("");
      }
    }
    $('#offcanvas input[name="duracion"]').val(data.duracion || "00:00");
    $("#offcanvas #tiempo-registrado-display").text(data.horas_trabajadas || "00:00");
  });
});

function actualizarTarea(data) {
  if (!currentTaskId) return;
  $.ajax({
    url: `../../api/tarea/${currentTaskId}/`,
    type: "PATCH",
    contentType: "application/json",
    headers: { "X-CSRFToken": csrfToken },
    data: JSON.stringify(data),
    success: function () {
      $("#table").DataTable().ajax.reload(null, false);
      $.NotificationApp.send("¡Actualizado!", "Cambios guardados", "bottom-right", "rgba(0,0,0,0.2)", "success");
    },
    error: function (xhr) {
      alert("Error al actualizar: " + (xhr.responseJSON?.error || xhr.statusText));
    },
  });
}

$('#offcanvas input[name="titulo"]').on("change", function () {
  actualizarTarea({ titulo: $(this).val() });
});

$('#offcanvas textarea[name="descripcion"]').on("change", function () {
  actualizarTarea({ descripcion: $(this).val() });
});

$('#offcanvas select[name="responsables"]').on("change", function () {
  actualizarTarea({ responsables: $(this).val() });
});

$('#offcanvas input[name="vencimiento"]').on("change", function () {
  actualizarTarea({ vencimiento: $(this).val() });
});

$('#offcanvas input[name="duracion"]').on("change", function () {
  actualizarTarea({ duracion_input: $(this).val() });
});
$('#offcanvas input[name="prioridad"]').on("change", function () {
  actualizarTarea({ prioridad: $(this).val() });
});

$("#table").on("click", "#drpEdit .dropdown-item", function (e) {
  e.preventDefault();
  var id = $(this).closest("tr").attr("id");
  var nuevoEstado = $(this).data("estado");
  $.ajax({
    type: "PATCH",
    url: `../../api/tarea/${id}/`,
    headers: { "X-CSRFToken": csrfToken },
    contentType: "application/json",
    dataType: "json",
    data: JSON.stringify({ estado: nuevoEstado }),
    success: function (data) {
      $("#table").DataTable().ajax.reload(null, false);
      $.NotificationApp.send("¡Bien Hecho!", "Estado actualizado correctamente", "bottom-right", "rgba(0,0,0,0.2)", "success");
    },
    error: function (xhr, status, error) {
      $.NotificationApp.send("¡Error!", "No se pudo actualizar el estado", "bottom-right", "rgba(0,0,0,0.2)", "danger");
    },
  });
});

$("#table").on("click", ".btn-delete-tarea", function () {
  var id = $(this).closest("tr").attr("id");
  $("#id_tarea_eliminar").val(id);
});

$("#frmDeleteTarea").on("submit", function (e) {
  e.preventDefault();
  var id_tarea = $("#id_tarea_eliminar").val();
  $.ajax({
    url: `../../api/tarea/${id_tarea}/`,
    type: "DELETE",
    headers: { "X-CSRFToken": csrfToken },
    success: function (response) {
      $("#table").DataTable().ajax.reload(null, false);
      $("#mdlDelete").modal("hide");
      $.NotificationApp.send("¡Bien Hecho!", "Tarea eliminada correctamente", "bottom-right", "rgba(0,0,0,0.2)", "success");
    },
    error: function (xhr) {
      $.NotificationApp.send("¡Error!", "No se pudo eliminar", "bottom-right", "rgba(0,0,0,0.2)", "danger");
    },
  });
});

function setScaleConfig(level) {
  switch (level) {
    case "day":
      gantt.config.scale_unit = "day";
      gantt.config.step = 1;
      gantt.config.date_scale = "%d %M"; // Día Mes (ej: 24 Oct)
      gantt.config.subscales = [
        { unit: "hour", step: 1, date: "%H:%i" }, // Hora:Minuto
      ];
      gantt.config.scale_height = 60;
      gantt.config.min_column_width = 40;
      break;
    case "week":
      gantt.config.scale_unit = "week";
      gantt.config.step = 1;
      gantt.config.date_scale = "Semana #%W"; // Semana del año
      gantt.config.subscales = [
        { unit: "day", step: 1, date: "%d %D" }, // Día y nombre corto (Lu, Ma...)
      ];
      gantt.config.scale_height = 60;
      gantt.config.min_column_width = 70;
      break;
    case "month":
      gantt.config.scale_unit = "month";
      gantt.config.date_scale = "%F %Y"; // Mes Año (ej: Octubre 2025)
      gantt.config.step = 1;
      gantt.config.subscales = [
        { unit: "week", step: 1, date: "#%W" }, // Semana #
      ];
      gantt.config.scale_height = 60;
      gantt.config.min_column_width = 100;
      break;
    case "year":
      gantt.config.scale_unit = "year";
      gantt.config.step = 1;
      gantt.config.date_scale = "%Y"; // Año (ej: 2025)
      gantt.config.subscales = [
        { unit: "month", step: 1, date: "%M" }, // Nombre corto del mes (Oct)
      ];
      gantt.config.scale_height = 60;
      gantt.config.min_column_width = 50;
      break;
  }
}

$(document).ready(function () {
  var ganttTab = document.querySelector('a[data-bs-toggle="tab"][href="#gantt"]');
  var isGanttInitialized = false;
  var ganttCurrentDate = new Date();
  if (ganttTab) {
    ganttTab.addEventListener("shown.bs.tab", function (event) {
      if (!isGanttInitialized) {
        // --- 1. Configuración de DHTMLX Gantt ---
        gantt.i18n.setLocale("es");

        gantt.config.columns = [
          { name: "text", label: "Descripción Actividad", tree: true, width: "*", resize: true },
          { name: "start_date", label: "Inicio", align: "center", width: 140 },
          { name: "end_date", label: "Fin", align: "center", width: 140 },
        ];

        gantt.config.show_progress = true;
        gantt.config.date_format = "%Y-%m-%d %H:%i:%s";

        // --- APLICA LA ESCALA INICIAL ANTES DE INIT ---
        setScaleConfig("month"); // <-- ESTABLECE 'MES' COMO INICIAL

        gantt.plugins({ tooltip: true });

        // --- [NUEVO] TRADUCCIÓN Y FORMATO DEL TOOLTIP ---
        gantt.templates.tooltip_text = function (start, end, task) {
          // Formateador de fecha (puedes cambiar "%Y-%m-%d" si prefieres otro formato)
          var formatFunc = gantt.date.date_to_str("%Y-%m-%d");
          var startDateStr = formatFunc(start);
          // DHTMLX calcula 'end' como el inicio del día *siguiente* si usas duration.
          // Para mostrar la fecha de fin correcta, restamos un día (o usamos la fecha fin de la API si la tuvieras directamente en el task object)
          // Como nuestra API devuelve end_date, ¡es más fácil! Pero necesitamos parsearla primero.
          var apiEndDate = gantt.date.parseDate(task.end_date, "%Y-%m-%d %H:%i:%s");
          // Si el parseo funcionó, la usamos, si no, calculamos restando 1 segundo al 'end' calculado por DHTMLX
          var displayEndDate = apiEndDate ? apiEndDate : gantt.date.add(end, -1, "second");
          var endDateStr = formatFunc(displayEndDate);

          return "<b>Tarea:</b> " + task.text + "<br/>" + "<b>Fecha Inicio:</b> " + startDateStr + "<br/>" + "<b>Fecha Fin:</b> " + endDateStr;
        };

        // --- [AQUÍ VA EL CÓDIGO DEL TEXTO A LA DERECHA] ---
        // 1. Vacía el texto DENTRO de la barra
        gantt.templates.task_text = function (start, end, task) {
          return ""; // No mostrar nada adentro
        };
        // 2. Muestra el texto completo a la DERECHA
        gantt.templates.rightside_text = function (start, end, task) {
          if (task.text) {
            // Asegúrate de que haya texto
            return task.text; // Muestra el nombre completo
          }
          return "";
        };
        // --- [FIN DEL CÓDIGO DEL TEXTO] ---

        // --- 2. Inicializar y Cargar Datos ---
        gantt.init("gantt_here");
        gantt.showDate(ganttCurrentDate);
        var container = document.getElementById("gantt_here");
        var urlGantt = container.getAttribute("data-json-url");
        gantt.load(urlGantt);
        isGanttInitialized = true;
      }
    });
  }

  // --- 3. Código de Navegación Mes a Mes ---
  $("#gantt_prev_month").on("click", function () {
    ganttCurrentDate.setMonth(ganttCurrentDate.getMonth() - 1);
    gantt.showDate(ganttCurrentDate);
  });

  $("#gantt_next_month").on("click", function () {
    ganttCurrentDate.setMonth(ganttCurrentDate.getMonth() + 1);
    gantt.showDate(ganttCurrentDate);
  });

  // --- 4. Código para Cambiar Escala/Zoom ---
  $("#gantt_scale_buttons").on("click", "button", function () {
    var scaleLevel = $(this).data("scale");

    $(this).addClass("active").siblings().removeClass("active");

    setScaleConfig(scaleLevel);

    gantt.render();
  });
});
