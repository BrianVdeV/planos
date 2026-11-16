import { api } from './api';
import type { Expediente, PaginatedResponse } from '@/types';

export const expedientesService = {
  /**
   * Lista general de expedientes (/api/expedientes/)
   */
  getExpedientes: async (
    params?: Record<string, unknown>
  ): Promise<PaginatedResponse<Expediente> | Expediente[]> => {
    const { data } = await api.get<PaginatedResponse<Expediente> | Expediente[]>(
      '/expedientes/',
      { params }
    );
    return data;
  },

  /**
   * Lista de expedientes Sunarp (/api/sunarp/)
   */
  getSunarp: async (
    params?: Record<string, unknown>
  ): Promise<PaginatedResponse<Expediente> | Expediente[]> => {
    const { data } = await api.get<PaginatedResponse<Expediente> | Expediente[]>(
      '/sunarp/',
      { params }
    );
    return data;
  },

  /**
   * Crea un expediente Sunarp (/api/sunarp/)
   */
  createSunarp: async (payload: Partial<Expediente>): Promise<Expediente> => {
    const { data } = await api.post<Expediente>('/sunarp/', payload);
    return data;
  },

  /**
   * Actualiza un expediente Sunarp (/api/sunarp/:id/)
   */
  updateSunarp: async (
    id: number,
    payload: Partial<Expediente>
  ): Promise<Expediente> => {
    const { data } = await api.patch<Expediente>(`/sunarp/${id}/`, payload);
    return data;
  },

  /**
   * Lista de expedientes de Municipalidad y Otros (/api/municipalidad/)
   */
  getMunicipalidad: async (
    params?: Record<string, unknown>
  ): Promise<PaginatedResponse<Expediente> | Expediente[]> => {
    const { data } = await api.get<PaginatedResponse<Expediente> | Expediente[]>(
      '/municipalidad/',
      { params }
    );
    return data;
  },

  /**
   * Crea un expediente de Municipalidad (/api/municipalidad/)
   */
  createMunicipalidad: async (payload: Partial<Expediente>): Promise<Expediente> => {
    const { data } = await api.post<Expediente>('/municipalidad/', payload);
    return data;
  },

  /**
   * Actualiza un expediente de Municipalidad (/api/municipalidad/:id/)
   */
  updateMunicipalidad: async (
    id: number,
    payload: Partial<Expediente>
  ): Promise<Expediente> => {
    const { data } = await api.patch<Expediente>(`/municipalidad/${id}/`, payload);
    return data;
  },
};
