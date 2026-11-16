import { api } from './api';
import type {
  Cotizacion,
  Gasto,
  PaginatedResponse,
  ReporteGasto,
} from '@/types';

export const gastosService = {
  /**
   * Lista de gastos (/api/gastos/)
   */
  getGastos: async (
    params?: Record<string, unknown>
  ): Promise<PaginatedResponse<Gasto> | Gasto[]> => {
    const { data } = await api.get<PaginatedResponse<Gasto> | Gasto[]>('/gastos/', {
      params,
    });
    return data;
  },

  /**
   * Crea un gasto (soporta FormData si lleva archivo comprobante)
   */
  createGasto: async (payload: Partial<Gasto> | FormData): Promise<Gasto> => {
    const headers =
      payload instanceof FormData
        ? { 'Content-Type': 'multipart/form-data' }
        : undefined;
    const { data } = await api.post<Gasto>('/gastos/', payload, { headers });
    return data;
  },

  /**
   * Actualiza un gasto (/api/gastos/:id/)
   */
  updateGasto: async (
    id: number,
    payload: Partial<Gasto> | FormData
  ): Promise<Gasto> => {
    const headers =
      payload instanceof FormData
        ? { 'Content-Type': 'multipart/form-data' }
        : undefined;
    const { data } = await api.patch<Gasto>(`/gastos/${id}/`, payload, {
      headers,
    });
    return data;
  },

  /**
   * Elimina un gasto (/api/gastos/:id/)
   */
  deleteGasto: async (id: number): Promise<void> => {
    await api.delete(`/gastos/${id}/`);
  },

  /**
   * Lista de reportes de gastos (/api/reportes/)
   */
  getReportes: async (
    params?: Record<string, unknown>
  ): Promise<PaginatedResponse<ReporteGasto> | ReporteGasto[]> => {
    const { data } = await api.get<
      PaginatedResponse<ReporteGasto> | ReporteGasto[]
    >('/reportes/', { params });
    return data;
  },

  /**
   * Actualiza el estado de un reporte de gasto (Aprobación / Rechazo)
   */
  updateReporte: async (
    id: number,
    payload: Partial<ReporteGasto>
  ): Promise<ReporteGasto> => {
    const { data } = await api.patch<ReporteGasto>(`/reportes/${id}/`, payload);
    return data;
  },

  /**
   * Obtiene el resumen de caja chica agrupada (/api/cajachica/)
   */
  getCajaChica: async (params?: Record<string, unknown>): Promise<unknown> => {
    const { data } = await api.get('/cajachica/', { params });
    return data;
  },

  /**
   * Lista de cotizaciones (/api/cotizaciones/)
   */
  getCotizaciones: async (
    params?: Record<string, unknown>
  ): Promise<PaginatedResponse<Cotizacion> | Cotizacion[]> => {
    const { data } = await api.get<PaginatedResponse<Cotizacion> | Cotizacion[]>(
      '/cotizaciones/',
      { params }
    );
    return data;
  },
};
