import http from './http'
import type { Subject, Course, EnrollmentRecord, CourseScore } from '@/types'

export const subjectApi = {
  list: () => http.get<Subject[]>('/api/subjects/'),
  courses: (subjectId: number) => http.get<Course[]>(`/api/subjects/${subjectId}/courses/`),
}

export const courseApi = {
  list: () => http.get<Course[]>('/api/courses/'),
  get: (courseId: number) => http.get<Course>(`/api/courses/${courseId}/`),
  myEnrollments: () => http.get<EnrollmentRecord[]>('/api/courses/my-enrollments/'),
  enroll: (courseId: number) => http.post(`/api/courses/${courseId}/enroll/`),
  myScores: () => http.get<CourseScore[]>('/api/courses/my-scores/'),
}
