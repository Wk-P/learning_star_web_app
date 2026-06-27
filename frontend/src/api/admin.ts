import http from './http'
import type { Subject, AdminUserDetail, BilibiliVideo } from '@/types'

// ── 科目管理 ──────────────────────────────────────────────────────────────────
export const adminSubjectApi = {
  list: () => http.get<Subject[]>('/api/admin/subjects/'),
  get: (id: number) => http.get<Subject>(`/api/admin/subjects/${id}/`),
  create: (data: Partial<Subject>) => http.post<Subject>('/api/admin/subjects/', data),
  update: (id: number, data: Partial<Subject>) => http.patch<Subject>(`/api/admin/subjects/${id}/`, data),
  delete: (id: number) => http.delete(`/api/admin/subjects/${id}/`),
  listVideos: (subjectId: number) =>
    http.get<BilibiliVideo[]>(`/api/admin/subjects/${subjectId}/videos/`),
  addVideo: (subjectId: number, data: { title: string; url: string }) =>
    http.post<BilibiliVideo>(`/api/admin/subjects/${subjectId}/videos/`, data),
  replaceVideos: (subjectId: number, videos: { title: string; url: string }[]) =>
    http.put<BilibiliVideo[]>(`/api/admin/subjects/${subjectId}/videos/`, videos),
  updateVideo: (subjectId: number, index: number, data: Partial<{ title: string; url: string }>) =>
    http.patch(`/api/admin/subjects/${subjectId}/videos/${index}/`, data),
  deleteVideo: (subjectId: number, index: number) =>
    http.delete(`/api/admin/subjects/${subjectId}/videos/${index}/`),
}

// ── 用户管理 ──────────────────────────────────────────────────────────────────
export const adminUserApi = {
  list: () => http.get<AdminUserDetail[]>('/api/admin/users/'),
  get: (userId: number) => http.get<AdminUserDetail>(`/api/admin/users/${userId}/`),
  create: (data: Partial<AdminUserDetail> & { password: string }) =>
    http.post<AdminUserDetail>('/api/admin/users/', data),
  update: (userId: number, data: Partial<AdminUserDetail>) =>
    http.patch<AdminUserDetail>(`/api/admin/users/${userId}/`, data),
  delete: (userId: number) => http.delete(`/api/admin/users/${userId}/`),
  resetPassword: (userId: number) =>
    http.post<{ newPassword: string }>(`/api/admin/users/${userId}/reset-password/`),
}
