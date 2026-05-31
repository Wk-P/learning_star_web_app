import http from './http'
import type {
  Subject,
  AdminUserDetail,
  Course,
  ClassSession,
  Homework,
  HomeworkSubmission,
  AttendanceRecord,
  EnrollmentRecord,
} from '@/types'

// ── 科目管理 ──────────────────────────────────────────────────────────────────
export const adminSubjectApi = {
  list: () => http.get<Subject[]>('/api/admin/subjects/'),
  get: (id: number) => http.get<Subject>(`/api/admin/subjects/${id}/`),
  create: (data: Partial<Subject>) => http.post<Subject>('/api/admin/subjects/', data),
  update: (id: number, data: Partial<Subject>) => http.patch<Subject>(`/api/admin/subjects/${id}/`, data),
  delete: (id: number) => http.delete(`/api/admin/subjects/${id}/`),
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

  // 某用户的课程关联
  enrollments: (userId: number) =>
    http.get<EnrollmentRecord[]>(`/api/admin/users/${userId}/enrollments/`),
  addEnrollment: (userId: number, courseId: number, enrolledAt?: string) =>
    http.post<EnrollmentRecord>(`/api/admin/users/${userId}/enrollments/`, { courseId, enrolledAt }),
  removeEnrollment: (userId: number, courseId: number) =>
    http.delete(`/api/admin/users/${userId}/enrollments/${courseId}/`),
  updateEnrollmentTime: (userId: number, courseId: number, enrolledAt: string) =>
    http.patch(`/api/admin/users/${userId}/enrollments/${courseId}/`, { enrolledAt }),

  // 某用户的作业提交
  homeworkList: (userId: number) =>
    http.get<HomeworkSubmission[]>(`/api/admin/users/${userId}/homework/`),
  gradeHomework: (userId: number, homeworkId: number, score: number) =>
    http.patch(`/api/admin/users/${userId}/homework/${homeworkId}/`, { score }),
}

// ── 课程管理 ──────────────────────────────────────────────────────────────────
export const adminCourseApi = {
  list: () => http.get<Course[]>('/api/admin/courses/'),
  get: (courseId: number) => http.get<Course>(`/api/admin/courses/${courseId}/`),
  create: (data: Partial<Course>) => http.post<Course>('/api/admin/courses/', data),
  update: (courseId: number, data: Partial<Course>) =>
    http.patch<Course>(`/api/admin/courses/${courseId}/`, data),
  delete: (courseId: number) => http.delete(`/api/admin/courses/${courseId}/`),

  // 出勤表
  attendance: (courseId: number, classId: number) =>
    http.get<AttendanceRecord[]>(`/api/admin/courses/${courseId}/classes/${classId}/attendance/`),
  updateAttendance: (courseId: number, classId: number, records: AttendanceRecord[]) =>
    http.put(`/api/admin/courses/${courseId}/classes/${classId}/attendance/`, records),

  // 课程文件
  uploadFile: (courseId: number, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return http.post(`/api/admin/courses/${courseId}/files/`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  deleteFile: (courseId: number, fileId: number) =>
    http.delete(`/api/admin/courses/${courseId}/files/${fileId}/`),
}

// ── 课节管理 ──────────────────────────────────────────────────────────────────
export const adminClassApi = {
  list: (courseId: number) =>
    http.get<ClassSession[]>(`/api/admin/courses/${courseId}/classes/`),
  generate: (courseId: number, clearExisting = true) =>
    http.post<{ count: number; sessions: ClassSession[] }>(
      `/api/admin/courses/${courseId}/classes/generate/`,
      { clearExisting, utcOffsetMinutes: -new Date().getTimezoneOffset() },
    ),
  get: (courseId: number, classId: number) =>
    http.get<ClassSession>(`/api/admin/courses/${courseId}/classes/${classId}/`),
  create: (courseId: number, data: Partial<ClassSession>) =>
    http.post<ClassSession>(`/api/admin/courses/${courseId}/classes/`, data),
  update: (courseId: number, classId: number, data: Partial<ClassSession>) =>
    http.patch<ClassSession>(`/api/admin/courses/${courseId}/classes/${classId}/`, data),
  delete: (courseId: number, classId: number) =>
    http.delete(`/api/admin/courses/${courseId}/classes/${classId}/`),
  uploadFile: (courseId: number, classId: number, file: File) => {
    const fd = new FormData(); fd.append('file', file)
    return http.post<import('@/types').CourseFile>(
      `/api/admin/courses/${courseId}/classes/${classId}/files/`, fd,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
  },
  deleteFile: (courseId: number, classId: number, fileId: number) =>
    http.delete(`/api/admin/courses/${courseId}/classes/${classId}/files/${fileId}/`),
}

// ── 作业管理 ──────────────────────────────────────────────────────────────────
export const adminHomeworkApi = {
  list: () => http.get<Homework[]>('/api/admin/homework/'),
  listByCourse: (courseId: number) =>
    http.get<Homework[]>(`/api/admin/courses/${courseId}/homework/`),
  get: (homeworkId: number) => http.get<Homework>(`/api/admin/homework/${homeworkId}/`),
  create: (data: Partial<Homework>) => http.post<Homework>('/api/admin/homework/', data),
  update: (homeworkId: number, data: Partial<Homework>) =>
    http.patch<Homework>(`/api/admin/homework/${homeworkId}/`, data),
  delete: (homeworkId: number) => http.delete(`/api/admin/homework/${homeworkId}/`),
  submissions: (homeworkId: number) =>
    http.get<HomeworkSubmission[]>(`/api/admin/homework/${homeworkId}/submissions/`),
  grade: (homeworkId: number, submissionId: number, score: number) =>
    http.patch<HomeworkSubmission>(
      `/api/admin/homework/${homeworkId}/submissions/${submissionId}/grade/`,
      { score },
    ),
}
