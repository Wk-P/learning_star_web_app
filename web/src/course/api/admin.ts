import http from './http'
import type { Subject, BilibiliVideo } from '@/course/types'

// ── 科目管理 ──────────────────────────────────────────────────────────────────
export const adminSubjectApi = {
  list: () => http.get<Subject[]>('/admin/subjects/'),
  get: (id: number) => http.get<Subject>(`/admin/subjects/${id}/`),
  create: (data: Partial<Subject>) => http.post<Subject>('/admin/subjects/', data),
  update: (id: number, data: Partial<Subject>) => http.patch<Subject>(`/admin/subjects/${id}/`, data),
  delete: (id: number) => http.delete(`/admin/subjects/${id}/`),
  listVideos: (subjectId: number) =>
    http.get<BilibiliVideo[]>(`/admin/subjects/${subjectId}/videos/`),
  addVideo: (subjectId: number, data: { line: string }) =>
    http.post<BilibiliVideo>(`/admin/subjects/${subjectId}/videos/`, data),
  replaceVideos: (subjectId: number, videos: { title: string; url: string }[]) =>
    http.put<BilibiliVideo[]>(`/admin/subjects/${subjectId}/videos/`, videos),
  updateVideo: (subjectId: number, index: number, data: Partial<{ title: string; url: string }>) =>
    http.patch(`/admin/subjects/${subjectId}/videos/${index}/`, data),
  deleteVideo: (subjectId: number, index: number) =>
    http.delete(`/admin/subjects/${subjectId}/videos/${index}/`),
}
