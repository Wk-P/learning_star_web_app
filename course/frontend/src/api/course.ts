import http from './http'
import type { Subject, BilibiliVideo } from '@/types'

export const subjectApi = {
  list: () => http.get<Subject[]>('/api/subjects/'),
  videos: (subjectId: number) => http.get<BilibiliVideo[]>(`/api/subjects/${subjectId}/videos/`),
}

export interface RoadmapMeta { exists: boolean; size?: number; updatedAt?: number }
export interface RoadmapContent { content: string; size: number; updatedAt: number }

export const roadmapApi = {
  get: () => http.get<RoadmapContent>('/api/roadmap/'),
  adminMeta: () => http.get<RoadmapMeta>('/api/admin/roadmap/'),
  adminUpload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return http.post<RoadmapMeta>('/api/admin/roadmap/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}
