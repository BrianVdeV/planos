import { api } from './api';
import type {
  PaginatedResponse,
  Ubicacion,
  UbicacionGeoJSONCollection,
  Ubigeo,
} from '@/types';

export const ubicacionesService = {
  /**
   * Obtiene todas las ubicaciones en formato GeoJSON (/api/ubicacion/geojson/)
   */
  getUbicacionesGeoJSON: async (): Promise<UbicacionGeoJSONCollection> => {
    const { data } = await api.get<UbicacionGeoJSONCollection>(
      '/ubicacion/geojson/'
    );
    return data;
  },

  /**
   * Lista de ubicaciones (/api/ubicacion/)
   */
  getUbicaciones: async (
    params?: Record<string, unknown>
  ): Promise<PaginatedResponse<Ubicacion> | UbicacionGeoJSONCollection> => {
    const { data } = await api.get<
      PaginatedResponse<Ubicacion> | UbicacionGeoJSONCollection
    >('/ubicacion/', { params });
    return data;
  },

  /**
   * Crea una nueva ubicación (/api/ubicacion/)
   */
  createUbicacion: async (payload: Partial<Ubicacion>): Promise<Ubicacion> => {
    const { data } = await api.post<Ubicacion>('/ubicacion/', payload);
    return data;
  },

  /**
   * Lista de departamentos (/api/ubigeo/departamentos/)
   */
  getDepartamentos: async (): Promise<string[]> => {
    const { data } = await api.get<string[]>('/ubigeo/departamentos/');
    return data;
  },

  /**
   * Lista de provincias por departamento (/api/ubigeo/provincias/?departamento=...)
   */
  getProvincias: async (departamento: string): Promise<string[]> => {
    const { data } = await api.get<string[]>('/ubigeo/provincias/', {
      params: { departamento },
    });
    return data;
  },

  /**
   * Lista de distritos por provincia (/api/ubigeo/?provincia=...)
   */
  getDistritos: async (
    provincia: string
  ): Promise<PaginatedResponse<Ubigeo> | Ubigeo[]> => {
    const { data } = await api.get<PaginatedResponse<Ubigeo> | Ubigeo[]>(
      '/ubigeo/',
      { params: { provincia } }
    );
    return data;
  },
};
