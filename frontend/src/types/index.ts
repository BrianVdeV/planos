// Respuesta paginada estándar de Django REST Framework
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ==========================================
// Autenticación y Usuarios
// ==========================================
export interface JWTTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface Area {
  id: number;
  nombre: string;
}

export interface Colaborador {
  id: number;
  usuario: number;
  nombres: string;
  apellidos: string;
  dni?: string;
  telefono?: string;
  correo?: string;
  foto?: string | null;
  area?: Area | null;
  estado?: boolean;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  is_superuser: boolean;
  is_staff?: boolean;
  is_active?: boolean;
  colaborador?: Colaborador | null;
}

// ==========================================
// Proyectos / OTs (Intranet)
// ==========================================
export interface TipoOT {
  id: number;
  nombre: string;
  codigo?: string;
}

export interface OT {
  id: number;
  id_str: string;
  codigo?: number;
  anio?: number;
  nombre: string;
  cliente?: string;
  estado: 'Activo' | 'Archivado' | 'Finalizado' | string;
  inicio?: string;
  fin?: string | null;
  presupuesto?: number | string;
  tipo?: number | TipoOT;
}

export interface HistogramaMensualResponse {
  promedio_mensual: number;
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
  }[];
}

// ==========================================
// Kanban, Tareas y Actividades
// ==========================================
export type EstadoTarea = 'todo' | 'in_progress' | 'review' | 'done';
export type PrioridadTarea = 'baja' | 'media' | 'alta' | 'urgente' | string;

export interface ResponsableInfo {
  id: number;
  username: string;
  foto: string;
}

export interface Tarea {
  id: number;
  titulo: string;
  descripcion?: string;
  estado: EstadoTarea;
  prioridad?: PrioridadTarea;
  orden?: number;
  ot: number;
  ot_str?: string;
  responsables: number[];
  responsables_info?: ResponsableInfo[];
  creado?: string;
  vencimiento?: string | null;
  duracion?: string | null;
  duracion_input?: string;
  horas_trabajadas?: string;
}

export interface Actividad {
  id: number;
  ot: number;
  ot_str?: string;
  tarea: number;
  tarea_str?: string;
  colaborador: number;
  comentario: string;
  inicio: string;
  fin?: string | null;
  duracion?: string | null;
  duracion_segundos?: number;
}

// ==========================================
// Calendario y Eventos
// ==========================================
export interface RecordatorioInput {
  cantidad: number;
  unidad: 'minutos' | 'horas' | 'dias';
}

export interface EventoCalendario {
  id: number | string;
  title: string;
  start: string;
  end?: string | null;
  allDay?: boolean;
  className?: string | string[];
  ot?: string | number | null;
  usuario?: string;
  descripcion?: string;
  recordatorio?: number | null;
}

export interface CrearEventoPayload {
  titulo: string;
  inicio: string;
  fin?: string | null;
  descripcion?: string;
  ot?: number | string | null;
  participantes?: number[];
  recordatorios?: RecordatorioInput[];
}

// ==========================================
// Expedientes (Sunarp y Municipalidad)
// ==========================================
export interface Expediente {
  id: number;
  numero?: string;
  anio?: number;
  ot: number;
  ot_str?: string;
  entidad?: 'SUNARP' | 'MUNICIPALIDAD' | string;
  oficina?: string;
  estado: string;
  presentacion?: string | null;
  reingreso?: string | null;
  vencimiento?: string | null;
  observacion?: string;
}

// ==========================================
// Gastos, Reportes y Cotizaciones
// ==========================================
export interface Gasto {
  id: number;
  ot?: number | null;
  ot_str?: string;
  descripcion: string;
  monto: number | string;
  moneda: 'PEN' | 'USD';
  fecha: string;
  comprobante?: string | null;
  estado?: 'Pendiente' | 'Aprobado' | 'Rechazado' | string;
  reporte?: number | null;
}

export interface ReporteGasto {
  id: number;
  titulo?: string;
  usuario: number;
  usuario_nombre?: string;
  fecha_creacion: string;
  estado: 'Pendiente' | 'Aprobado' | 'Rechazado' | string;
  total: number | string;
  gastos?: Gasto[];
  motivo_rechazo?: string;
}

export interface Cotizacion {
  id: number;
  numero?: string;
  cliente: string;
  proyecto?: string;
  monto: number | string;
  moneda: 'PEN' | 'USD';
  estado: string;
  fecha: string;
}

// ==========================================
// Ubicaciones y GeoJSON
// ==========================================
export interface Ubigeo {
  id: number;
  codigo?: string;
  departamento: string;
  provincia: string;
  distrito: string;
}

export interface Ubicacion {
  id: number;
  ot: number;
  ot_str?: string;
  ubigeo: number;
  direccion: string;
  coordenadas?: string;
  latitud?: number;
  longitud?: number;
}

export interface UbicacionGeoJSONFeature {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: [number, number]; // [lng, lat]
  };
  properties: {
    id: string | number;
    ot: string;
    nac_ot?: number;
    departamento: string;
    provincia: string;
    distrito: string;
    direccion: string;
  };
}

export interface UbicacionGeoJSONCollection {
  type: 'FeatureCollection';
  features: UbicacionGeoJSONFeature[];
}

// ==========================================
// Notificaciones y Sidebar Badges
// ==========================================
export interface SidebarBadges {
  agenda: number;
  pending: number;
  rejected: number;
}

export interface NotificacionToast {
  id?: number;
  titulo: string;
  descripcion: string;
  tipo?: 'warning' | 'success' | 'error' | 'info';
}

export interface WebSocketNotificationEvent {
  tipo: 'actualizacion_expediente' | 'nuevo_reporte_admin' | 'reporte_rechazado' | string;
  titulo: string;
  cuerpo: string;
  ot_id?: string | number;
  expediente_id?: number;
  estado?: string;
  entidad?: string;
  usuario_id?: number;
  reporte_id?: number;
}
