socket.onmessage = function (e) {
  const data = JSON.parse(e.data);
  if (data.tipo === "activity-stopped") {
    mostrarAlerta(
      `Hora del Almuerzo`,
      `Se detuvo la actividad ⏸️`,
      `actividad`,
    );
    $.NotificationApp.send(
      "¡ATENCIÓN! 🛑",
      data.message + " La página se recargará en 3 segundos.",
      "top-center",
      "rgba(0,0,0,0.2)",
      "error",
    );
    setTimeout(function () {
      location.reload();
    }, 3000);
  }
};

// ============================================
// TOUR GUIADO CON SHEPHERD.JS - MÓDULO INICIO
// ============================================
const tourInicio = new Shepherd.Tour({
  useModalOverlay: true,
  defaultStepOptions: {
    classes: "shadow-lg",
    scrollTo: { behavior: "smooth", block: "center" },
    cancelIcon: {
      enabled: true,
    },
  },
});
// Paso 1: Seleccionar OT
tourInicio.addStep({
  id: "paso-select-ot",
  text: `<h5 class="mb-2">📋 Seleccione la OT</h5>
           <p>Seleccione la <strong>Orden de Trabajo (OT)</strong> correspondiente a la actividad que realizará.</p>
           <p class="text-danger mb-0"><strong>⚠️ Este campo es OBLIGATORIO.</strong></p>`,
  attachTo: {
    element: "#sltOT",
    on: "bottom",
  },
  buttons: [
    {
      text: "Salir",
      action: tourInicio.cancel,
      classes: "btn btn-sm btn-secondary",
    },
    {
      text: "Siguiente",
      action: tourInicio.next,
      classes: "btn btn-sm btn-primary",
    },
  ],
});

// Paso 2: Seleccionar Actividad
tourInicio.addStep({
  id: "paso-select-actividad",
  text: `<h5 class="mb-2">🎯 Seleccione la Actividad</h5>
           <p>Debe marcar la actividad de acuerdo a <strong>la tarea que se le ha asignado</strong>.</p>
           <p class="mb-0">Asegúrese de seleccionar la actividad correcta según su asignación.</p>`,
  attachTo: {
    element: "#sltTarea",
    on: "bottom",
  },
  buttons: [
    {
      text: "Anterior",
      action: tourInicio.back,
      classes: "btn btn-sm btn-secondary",
    },
    {
      text: "Siguiente",
      action: tourInicio.next,
      classes: "btn btn-sm btn-primary",
    },
  ],
});

// Paso 3: Anotaciones y Descripción
tourInicio.addStep({
  id: "paso-descripcion",
  text: `<h5 class="mb-2">📝 Anotaciones y Descripción</h5>
           <p>Usted pondrá una <strong>descripción de la actividad que realizará</strong> que sea entendible.</p>
           <p>Al acabar con esta actividad, lo podrá modificar en caso de que requiera que sea más detallada.</p>
           <p class="text-info mb-0"><strong>💡 Debe tener entre 5 y 300 caracteres.</strong></p>`,
  attachTo: {
    element: "#txtActividades",
    on: "bottom",
  },
  buttons: [
    {
      text: "Anterior",
      action: tourInicio.back,
      classes: "btn btn-sm btn-secondary",
    },
    {
      text: "Siguiente",
      action: tourInicio.next,
      classes: "btn btn-sm btn-primary",
    },
  ],
});

// Paso 4: Botón Iniciar
tourInicio.addStep({
  id: "paso-boton-iniciar",
  text: `<h5 class="mb-2">▶️ Botón Iniciar</h5>
           <p>Una vez ya seleccionada su <strong>OT</strong>, <strong>Actividad</strong> y la <strong>Descripción</strong> correspondiente, presione este botón de <strong>Iniciar</strong>.</p>
           <p class="mb-0">Esto comenzará el registro de tiempo de su actividad.</p>`,
  attachTo: {
    element: "#btnIniciar",
    on: "left",
  },
  buttons: [
    {
      text: "Anterior",
      action: tourInicio.back,
      classes: "btn btn-sm btn-secondary",
    },
    {
      text: "Siguiente",
      action: tourInicio.next,
      classes: "btn btn-sm btn-primary",
    },
  ],
});

// Paso 5: Botón Reanudar (en la tabla)
tourInicio.addStep({
  id: "paso-boton-reanudar",
  text: `<h5 class="mb-2">🔄 Botón Reanudar Actividad</h5>
           <p>Presione este botón de <strong>Reanudar Actividad</strong> en caso de que desee continuar con la misma actividad.</p>
           <p class="mb-0">Esto evita que tenga que seleccionar y escribir todo otra vez.</p>`,
  attachTo: {
    element: "#columnaReanudar",
    on: "bottom",
  },
  buttons: [
    {
      text: "Anterior",
      action: tourInicio.back,
      classes: "btn btn-sm btn-secondary",
    },
    {
      text: "Siguiente",
      action: tourInicio.next,
      classes: "btn btn-sm btn-primary",
    },
  ],
});

// Paso 6: Recordatorio de Horarios
tourInicio.addStep({
  id: "paso-recordatorio-horarios",
  text: `<h5 class="mb-3 text-center">⏰ RECORDATORIO IMPORTANTE</h5>
           <div class="alert alert-warning mb-2">
             <strong>Horario de Inicio:</strong>
             <p class="mb-0">Debe iniciar su actividad a las <strong>8:00 AM</strong></p>
           </div>
           <div class="alert alert-danger mb-2">
             <strong>Hora de Almuerzo:</strong>
             <p class="mb-1">Debe detener su actividad a las <strong>1:00 PM</strong> o a la hora designada por administración.</p>
             <p class="mb-0">Si salió a hacer un trámite en la mañana, deténgala a la hora que llegue para almorzar.</p>
           </div>
           <div class="alert alert-success mb-2">
             <strong>Regreso del Almuerzo:</strong>
             <p class="mb-0">Debe volver a iniciar su actividad <strong>50 minutos después</strong>, es decir: <strong>1:50 PM</strong> o la hora que se le fue designada, o su hora de llegada.</p>
           </div>
           <div class="alert alert-info mb-3">
             <strong>Hora de Salida:</strong>
             <p class="mb-0">Debe finalizar su actividad a las <strong>6:30 PM</strong> o la hora que saldrá en caso de quedarse a hacer horas extra.</p>
           </div>
           <p class="text-danger text-center mb-0"><strong>⚠️ Recuerde esto con atención: se evaluará todo el registro de sus actividades.</strong></p>`,
  attachTo: {
    element: "body",
    on: "center",
  },
  buttons: [
    {
      text: "Anterior",
      action: tourInicio.back,
      classes: "btn btn-sm btn-secondary",
    },
    {
      text: "Finalizar",
      action: tourInicio.complete,
      classes: "btn btn-sm btn-success",
    },
  ],
});

// Iniciar el tour cuando se hace clic en el botón de ayuda
document
  .getElementById("btnAyudaInicio")
  .addEventListener("click", function () {
    tourInicio.start();
  });
