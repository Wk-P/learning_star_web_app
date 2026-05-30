import http from './http'
import type { TokenPair, LoginPayload, User } from '@/types'

export const authApi = {
  login: (payload: LoginPayload) =>
    http.post<TokenPair>('/api/token/', payload),

  refresh: (refresh: string) =>
    http.post<TokenPair>('/api/token/refresh/', { refresh }),

  me: () => http.get<User>('/api/users/me/'),

  changePassword: (oldPassword: string, newPassword: string) =>
    http.post('/api/users/me/change-password/', { oldPassword, newPassword }),
}

export const updateDisplayName = (displayName: string) => {
  return http.patch('/api/users/me/update-display/', { displayName });
}
