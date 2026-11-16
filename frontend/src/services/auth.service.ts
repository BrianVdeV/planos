import { api } from './api';
import type {
  Area,
  Colaborador,
  JWTTokens,
  LoginCredentials,
  PaginatedResponse,
  User,
} from '@/types';

export const authService = {
  /**
   * Obtiene el par de tokens JWT (access y refresh) desde djangorestframework-simplejwt
   */
  login: async (credentials: LoginCredentials): Promise<JWTTokens> => {
    const { data } = await api.post<JWTTokens>('/token/', credentials);
    return data;
  },

  /**
   * Refresca el access token usando el refresh token
   */
  refreshToken: async (refresh: string): Promise<{ access: string }> => {
    const { data } = await api.post<{ access: string }>('/token/refresh/', {
      refresh,
    });
    return data;
  },

  /**
   * Lista de usuarios del sistema (/api/users/)
   */
  getUsers: async (params?: Record<string, unknown>): Promise<PaginatedResponse<User> | User[]> => {
    const { data } = await api.get<PaginatedResponse<User> | User[]>('/users/', {
      params,
    });
    return data;
  },

  /**
   * Obtiene el detalle de un usuario por ID
   */
  getUserById: async (id: number): Promise<User> => {
    const { data } = await api.get<User>(`/users/${id}/`);
    return data;
  },

  /**
   * Lista de colaboradores (/api/colaboradores/)
   */
  getColaboradores: async (
    params?: Record<string, unknown>
  ): Promise<PaginatedResponse<Colaborador> | Colaborador[]> => {
    const { data } = await api.get<PaginatedResponse<Colaborador> | Colaborador[]>(
      '/colaboradores/',
      { params }
    );
    return data;
  },

  /**
   * Lista de áreas (/api/area/)
   */
  getAreas: async (): Promise<PaginatedResponse<Area> | Area[]> => {
    const { data } = await api.get<PaginatedResponse<Area> | Area[]>('/area/');
    return data;
  },
};
