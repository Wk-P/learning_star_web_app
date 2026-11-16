import http, { withIndex } from './http'
import type { Subject, BilibiliVideo } from '@/course/types'

export const subjectApi = {
  list: () => http.get<Subject[]>('/subjects/'),
  videos: (subjectId: number) =>
    http.get<Omit<BilibiliVideo, 'index'>[]>(`/subjects/${subjectId}/videos/`).then(withIndex),
}
