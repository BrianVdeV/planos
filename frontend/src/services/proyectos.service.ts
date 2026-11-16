import { api } from './api';
import type {
  HistogramaMensualResponse,
  OT,
  PaginatedResponse,
  TipoOT,
} from '@/types';

export const proyectosService = {
  /**
   * Lista o busca OTs (/api/ots/)
   */
  getOTs: async (
    params?: Record<string, unknown>
  ): Promise<PaginatedResponse<OT> | OT[]> => {
    const { data } = await api.get<PaginatedResponse<OT> | OT[]>('/ots/', {
      params,
    });
    return data;
  },

  /**
   * Obtiene el detalle de una OT por su ID
   */
  getOTById: async (id: number | string): Promise<OT> => {
    const { data } = await api.get<OT>(`/ots/${id}/`);
    return data;
  },

  /**
   * Crea una nueva OT
   */
  createOT: async (payload: Partial<OT>): Promise<OT> => {
    const { data } = await api.post<OT>('/ots/', payload);
    return data;
  },

  /**
   * Actualiza parcialmente una OT
   */
  updateOT: async (id: number | string, payload: Partial<OT>): Promise<OT> => {
    const { data } = await api.patch<OT>(`/ots/${id}/`, payload);
    return data;
  },

  /**
   * Elimina una OT
   */
  deleteOT: async (id: number | string): Promise<void> => {
    await api.delete(`/ots/${id}/`);
  },

  /**
   * Obtiene el histograma mensual de OTs para el Dashboard (/api/ots/histograma_mensual/)
   */
  getHistogramaMensual: async (
    year: number | string
  ): Promise<HistogramaMensualResponse> => {
    const { data } = await api.get<HistogramaMensualResponse>(
      '/ots/histograma_mensual/',
      { params: { year } }
    );
    return data;
  },

  /**
   * Obtiene las últimas OTs creadas (/api/ots/recientes/)
   */
  getOTsRecientes: async (): Promise<OT[]> => {
    const { data } = await api.get<OT[]>('/ots/recientes/');
    return data;
  },

  /**
   * Obtiene los tipos de OT (/api/tipot/)
   */
  getTiposOT: async (): Promise<PaginatedResponse<TipoOT> | TipoOT[]> => {
    const { data } = await api.get<PaginatedResponse<TipoOT> | TipoOT[]>('/tipot/');
    return data;
  },
};
