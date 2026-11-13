if (
  Notification.permission !== "granted" &&
  Notification.permission !== "denied"
) {
  Notification.requestPermission();
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const colorMapping = {
  Presentado: "#00a7a4",
  Reingresado: "#1d58b4",
  Apelado: "#ef8e00",
  "En proceso": "#b4b4b4",
  "En calificación": "#5a2071",
  "En calificacion": "#5a2071",
  Inscrito: "#89be21",
  Reservado: "#575756",
  Distribuido: "#f31c53",
  Liquidado: "#006633",
  Prorrogado: "#80d0ff",
  Observado: "red",
  Suspendido: "#981622",
  Tachado: "black",
  "Res. Tribunal": "black",
  "Res. Procedente": "#006633",
  "Res. Improcedente": "black",
  Anotado: "#7eb3d5",
  Finalizado: "#89be21",
};

const drpConfig = {
  ranges: {
    Hoy: [moment(), moment()],
    Ayer: [moment().subtract(1, "days"), moment().subtract(1, "days")],
    "Esta semana": [moment().startOf("week"), moment().endOf("week")],
    "La semana pasada": [
      moment().subtract(1, "week").startOf("week"),
      moment().subtract(1, "week").endOf("week").subtract(0, "days"),
    ],
    "Este mes": [moment().startOf("month"), moment().endOf("month")],
    "El mes pasado": [
      moment().subtract(1, "month").startOf("month"),
      moment().subtract(1, "month").endOf("month"),
    ],
    "Este año": [moment().startOf("year"), moment().endOf("year")],
  },
  locale: {
    format: "DD/MM/YYYY",
    separator: " - ",
    applyLabel: "Aplicar",
    cancelLabel: "Cancelar",
    daysOfWeek: ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa"],
    monthNames: [
      "Enero",
      "Febrero",
      "Marzo",
      "Abril",
      "Mayo",
      "Junio",
      "Julio",
      "Agosto",
      "Septiembre",
      "Octubre",
      "Noviembre",
      "Diciembre",
    ],
    firstDay: 0,
  },
  alwaysShowCalendars: true,
  showCustomRangeLabel: false,
  opens: "left",
  autoApply: true,
  format: "YYYY-MM-DD",
};

function jqueryToast(
  titulo = "¡Bien Hecho!",
  mensaje,
  posicion = "bottom-right",
  tipo = "success",
  duracion = 3000,
) {
  $.toast({
    heading: titulo,
    text: mensaje,
    position: posicion,
    icon: tipo, // warning, success, error, info
    loaderBg: "rgba(0,0,0,0.2)",
    hideAfter: duracion,
  });
}

const wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
const wsUrl = wsProtocol + window.location.host + "/ws/notificaciones/";
const socket = new WebSocket(wsUrl);

// Funciones auxiliares para no repetir código
function reproducirVoz(texto) {
  const mensajeVoz = new SpeechSynthesisUtterance(texto);
  mensajeVoz.lang = "es-ES";
  mensajeVoz.rate = 1.0;
  mensajeVoz.pitch = 1.0;
  window.speechSynthesis.speak(mensajeVoz);
}

function mostrarAlerta(titulo, cuerpo, tag) {
  new Notification(titulo, {
    body: cuerpo,
    tag: tag,
    requireInteraction: true,
  });
}

function lanzarNotificacionActividades(titulo, cuerpo) {
  if (Notification.permission === "granted") {
    const notificacion = new Notification(titulo, {
      body: cuerpo,
      requireInteraction: true,
    });
    notificacion.onclick = function (event) {
      event.preventDefault();
      window.focus();
      const urlDestino = "https://intranet.planosperu.com.pe/actividades/";
      if (!window.location.href.includes("/actividades")) {
        window.location.href = urlDestino;
      }

      notificacion.close();
    };

    reproducirVoz(cuerpo);
  }
}

// 3. Función para calcular el tiempo y programar la alerta
function programarAlarmaDiaria(hora, minuto, titulo, cuerpo) {
  const ahora = new Date();
  let tiempoDestino = new Date(
    ahora.getFullYear(),
    ahora.getMonth(),
    ahora.getDate(),
    hora,
    minuto,
    0,
    0,
  );
  let delay = tiempoDestino.getTime() - ahora.getTime();
  if (delay < 0) {
    tiempoDestino.setDate(tiempoDestino.getDate() + 1);
    delay = tiempoDestino.getTime() - ahora.getTime();
  }
  setTimeout(() => {
    lanzarNotificacionActividades(titulo, cuerpo);
    programarAlarmaDiaria(hora, minuto, titulo, cuerpo);
  }, delay);
}

// 4. Inicializar las 3 alarmas solicitadas
programarAlarmaDiaria(
  13,
  50,
  "Cierre del Almuerzo",
  "Son las 1:50 PM. Toca aquí para ir al panel de actividades antes del corte.",
);
programarAlarmaDiaria(
  18,
  30,
  "Fin de Jornada",
  "Son las 6:30 PM. Toca para registrar tu fin de actividad.",
);

socket.onmessage = function (e) {
  const data = JSON.parse(e.data);

  // ESCENARIO 1: Viene una notificación de un Expediente (Global)
  if (data.tipo === "actualizacion_expediente") {
    const textoALeer = `Atención. El expediente de la OT ${data.ot_id} ha sido actualizado al estado: ${data.estado}.`;

    reproducirVoz(textoALeer);
    mostrarAlerta(
      `Expediente OT ${data.ot_id} Actualizado`,
      `Nuevo estado: ${data.estado}\nEntidad: ${data.entidad}`,
      `exp_${data.expediente_id}`,
    );
  }

  // ESCENARIO 2: Viene un nuevo Reporte de Gastos (Solo para Admins)
  else if (data.tipo === "nuevo_reporte_admin") {
    const textoALeer = `Administrador, tienes nuevas solicitudes de gastos de ${data.cuerpo.split(" ")[0]}.`;

    reproducirVoz(textoALeer);
    mostrarAlerta(data.titulo, data.cuerpo, `gastos_${data.usuario_id}`);
  } else if (data.tipo === "reporte_rechazado") {
    const textoALeer =
      "Atención. Uno de tus reportes de gastos ha sido rechazado.";

    reproducirVoz(textoALeer);
    mostrarAlerta(data.titulo, data.cuerpo, `rechazo_${data.reporte_id}`);
  }

  // Puedes agregar más escenarios aquí según tus modelos ("mensaje_chat", "alerta_sistema", etc.)
};
