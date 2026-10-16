import http from './http'
import type { Subject, BilibiliVideo } from '@/course/types'

export const subjectApi = {
  list: () => http.get<Subject[]>('/subjects/'),
  videos: (subjectId: number) => http.get<BilibiliVideo[]>(`/subjects/${subjectId}/videos/`),
}

export interface RoadmapMeta { exists: boolean; size?: number; updatedAt?: number }
export interface RoadmapContent { content: string; size: number; updatedAt: number }

export const roadmapApi = {
  get: () => http.get<RoadmapContent>('/roadmap/'),
  adminMeta: () => http.get<RoadmapMeta>('/admin/roadmap/'),
  adminUpload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return http.post<RoadmapMeta>('/admin/roadmap/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}
