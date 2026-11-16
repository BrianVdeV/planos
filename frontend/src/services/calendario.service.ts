import { api } from './api';
import type {
  CrearEventoPayload,
  EventoCalendario,
  PaginatedResponse,
} from '@/types';

export const calendarioService = {
  /**
   * Obtiene los eventos del calendario (/api/calendario/)
   */
  getEventos: async (
    params?: Record<string, unknown>
  ): Promise<PaginatedResponse<EventoCalendario> | EventoCalendario[]> => {
    const { data } = await api.get<
      PaginatedResponse<EventoCalendario> | EventoCalendario[]
    >('/calendario/', { params });
    return data;
  },

  /**
   * Crea un nuevo evento con recordatorios (/api/eventos/)
   */
  createEvento: async (payload: CrearEventoPayload): Promise<EventoCalendario> => {
    const { data } = await api.post<EventoCalendario>('/eventos/', payload);
    return data;
  },

  /**
   * Elimina un evento (/api/eventos/:id/)
   */
  deleteEvento: async (id: number | string): Promise<void> => {
    await api.delete(`/eventos/${id}/`);
  },
};
