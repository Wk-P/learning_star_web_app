import http from './http'
import type { Subject, BilibiliVideo } from '@/course/types'

export const subjectApi = {
  list: () => http.get<Subject[]>('/subjects/'),
  videos: (subjectId: number) => http.get<BilibiliVideo[]>(`/subjects/${subjectId}/videos/`),
}
