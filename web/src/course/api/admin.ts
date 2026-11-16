import http, { withIndex } from './http'
import type { Subject, BilibiliVideo, VideoLevel } from '@/course/types'

// ── 科目管理 ──────────────────────────────────────────────────────────────────
export const adminSubjectApi = {
  list: () => http.get<Subject[]>('/admin/subjects/'),
  get: (id: number) => http.get<Subject>(`/admin/subjects/${id}/`),
  create: (data: Partial<Subject>) => http.post<Subject>('/admin/subjects/', data),
  update: (id: number, data: Partial<Subject>) => http.patch<Subject>(`/admin/subjects/${id}/`, data),
  delete: (id: number) => http.delete(`/admin/subjects/${id}/`),
  listVideos: (subjectId: number) =>
    http.get<Omit<BilibiliVideo, 'index'>[]>(`/admin/subjects/${subjectId}/videos/`).then(withIndex),
  addVideo: (subjectId: number, data: { line: string; levels: VideoLevel[]; tags: string[] }) =>
    http.post<BilibiliVideo>(`/admin/subjects/${subjectId}/videos/`, data),
  updateVideo: (subjectId: number, videoId: number, data: Partial<{ title: string; url: string; levels: VideoLevel[]; tags: string[] }>) =>
    http.patch(`/admin/subjects/${subjectId}/videos/${videoId}/`, data),
  deleteVideo: (subjectId: number, videoId: number) =>
    http.delete(`/admin/subjects/${subjectId}/videos/${videoId}/`),
}
