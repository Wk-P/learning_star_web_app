import { useAuthStore } from '@/stores/auth'

// 生产环境由 .env.production 设为 /topik，开发环境走 vite 代理
const BASE = `${import.meta.env.VITE_API_PREFIX ?? ''}/api`

async function refreshAccessToken(): Promise<boolean> {
  const auth = useAuthStore()
  if (!auth.refreshToken) return false
  try {
    const res = await fetch(`${BASE}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: auth.refreshToken }),
    })
    if (!res.ok) return false
    const data = await res.json()
    auth.setTokens(data.access, auth.refreshToken)
    return true
  } catch {
    return false
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const auth = useAuthStore()
  const makeHeaders = () => ({
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
    ...(auth.accessToken ? { Authorization: `Bearer ${auth.accessToken}` } : {}),
  })

  let res = await fetch(`${BASE}${path}`, { ...options, headers: makeHeaders() })

  if (res.status === 401) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      res = await fetch(`${BASE}${path}`, { ...options, headers: makeHeaders() })
    } else {
      auth.clearTokens()
      window.location.href = `${import.meta.env.BASE_URL}login`
      throw res
    }
  }

  if (!res.ok) throw res
  return res.json()
}

export const api = {
  login(username: string, password: string) {
    return request<{ access: string; refresh: string }>('/auth/token/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  },

  register(username: string, password: string) {
    return request<UserItem>('/user/register/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  },

  getVideoList() {
    return request<{ id: number; path: string[]; videos: VideoItem[] }[]>('/video/list/')
  },

  getVideo(id: number) {
    return request<VideoItem>(`/video/detail/?id=${id}`)
  },

  getAudioList() {
    return request<{ id: number; path: string[]; audios: AudioItem[] }[]>('/audio/list/')
  },

  getAudio(id: number) {
    return request<AudioItem>(`/audio/detail/?id=${id}`)
  },

  getPdfList() {
    return request<{ id: number; path: string[]; pdfs: PdfItem[] }[]>('/pdf/list/')
  },

  getPdf(id: number) {
    return request<PdfItem>(`/pdf/detail/?id=${id}`)
  },

  // admin: user management
  getUserList() {
    return request<UserItem[]>('/user/')
  },
  createUser(data: { username: string; password: string; email?: string }) {
    return request<UserItem>('/user/create/', { method: 'POST', body: JSON.stringify(data) })
  },
  deleteUser(id: number) {
    return request<void>(`/user/${id}/delete/`, { method: 'DELETE' })
  },
  resetUserPassword(id: number, newPassword: string) {
    return request<{ detail: string }>(`/user/${id}/reset-password/`, {
      method: 'POST',
      body: JSON.stringify({ new_password: newPassword }),
    })
  },

  // admin: permissions
  getMediaRoots() {
    return request<{ video: string[]; audio: string[]; pdf: string[] }>('/permission/roots/')
  },
  getMediaTree() {
    return request<{ video: TreeNode[]; audio: TreeNode[]; pdf: TreeNode[] }>('/permission/tree/')
  },
  getUserPermissions(userId: number) {
    return request<{ video: string[]; audio: string[]; pdf: string[] }>(`/permission/users/${userId}/`)
  },
  setUserPermissions(userId: number, data: { video: string[]; audio: string[]; pdf: string[] }) {
    return request<{ video: string[]; audio: string[]; pdf: string[] }>(`/permission/users/${userId}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  getMe() {
    return request<{ username: string; is_staff: boolean }>('/user/me/')
  },

  getMyPermissions() {
    return request<{ video: string[]; audio: string[]; pdf: string[] }>('/user/me/permissions/')
  },

  changePassword(oldPassword: string, newPassword: string) {
    return request<{ detail: string }>('/user/me/password/', {
      method: 'POST',
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    })
  },
}

export interface VideoItem {
  id: number
  title: string
  url: string
}

export interface AudioItem {
  id: number
  title: string
  url: string
}

export interface PdfItem {
  id: number
  title: string
  url: string
}

export interface UserItem {
  id: number
  username: string
  email: string
  is_staff: boolean
}

export interface TreeNode {
  path: string
  label: string
  children: TreeNode[]
}
