import http from './http'
import type { Subject, BilibiliVideo } from '@/types'

export const subjectApi = {
  list: () => http.get<Subject[]>('/api/subjects/'),
  videos: (subjectId: number) => http.get<BilibiliVideo[]>(`/api/subjects/${subjectId}/videos/`),
}
