import { useAuthStore } from '@/stores/auth'

const BASE = '/api'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const auth = useAuthStore()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  if (auth.accessToken) {
    headers['Authorization'] = `Bearer ${auth.accessToken}`
  }
  const res = await fetch(`${BASE}${path}`, { ...options, headers })
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

  // admin: permissions
  getMediaRoots() {
    return request<{ video: string[]; audio: string[]; pdf: string[] }>('/permission/roots/')
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
