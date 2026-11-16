import { request, json } from '@/core/api/http'

export interface UserItem {
  id: number
  username: string
  email: string | null
  display_name: string
  is_staff: boolean
  is_active: boolean
  date_joined: string
}

export const accountsApi = {
  login(username: string, password: string) {
    return request<{ access: string; refresh: string }>('/auth/token/', json('POST', { username, password }))
  },
  register(username: string, password: string) {
    return request<UserItem>('/accounts/register/', json('POST', { username, password }))
  },
  me() {
    return request<UserItem>('/accounts/me/')
  },
  updateMe(data: { display_name: string }) {
    return request<UserItem>('/accounts/me/', json('PATCH', data))
  },
  changePassword(oldPassword: string, newPassword: string) {
    return request<{ detail: string }>('/accounts/me/password/', json('POST', { old_password: oldPassword, new_password: newPassword }))
  },

  // ── 管理员 ──
  listUsers() {
    return request<UserItem[]>('/accounts/users/')
  },
  createUser(data: { username: string; password: string; email?: string }) {
    return request<UserItem>('/accounts/users/', json('POST', data))
  },
  deleteUser(id: number) {
    return request<void>(`/accounts/users/${id}/`, json('DELETE'))
  },
  resetUserPassword(id: number, newPassword: string) {
    return request<{ detail: string }>(`/accounts/users/${id}/reset-password/`, json('POST', { new_password: newPassword }))
  },
}
