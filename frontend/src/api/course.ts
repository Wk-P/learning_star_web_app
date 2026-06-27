import http from './http'
import type { Subject, Course, BilibiliVideo } from '@/types'

export const subjectApi = {
  list: () => http.get<Subject[]>('/api/subjects/'),
  courses: (subjectId: number) => http.get<Course[]>(`/api/subjects/${subjectId}/courses/`),
  videos: (subjectId: number) => http.get<BilibiliVideo[]>(`/api/subjects/${subjectId}/videos/`),
}

export const courseApi = {
  list: () => http.get<Course[]>('/api/courses/'),
  get: (courseId: number) => http.get<Course>(`/api/courses/${courseId}/`),
}
