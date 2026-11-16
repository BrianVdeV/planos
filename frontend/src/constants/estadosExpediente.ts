/**
 * Mapeo oficial de colores para los estados de expedientes (migrado de backend/static/js/scripts.js)
 */
export const ESTADO_EXPEDIENTE_COLOR_MAP: Record<string, string> = {
  Presentado: '#00a7a4',
  Reingresado: '#1d58b4',
  Apelado: '#ef8e00',
  'En proceso': '#b4b4b4',
  'En calificación': '#5a2071',
  'En calificacion': '#5a2071',
  Inscrito: '#89be21',
  Reservado: '#575756',
  Distribuido: '#f31c53',
  Liquidado: '#006633',
  Prorrogado: '#80d0ff',
  Observado: '#ef4444',
  Suspendido: '#981622',
  Tachado: '#000000',
  'Res. Tribunal': '#000000',
  'Res. Procedente': '#006633',
  'Res. Improcedente': '#000000',
  Anotado: '#7eb3d5',
  Finalizado: '#89be21',
};

export function getEstadoExpedienteColor(estado: string): string {
  return ESTADO_EXPEDIENTE_COLOR_MAP[estado] ?? '#64748b';
}
