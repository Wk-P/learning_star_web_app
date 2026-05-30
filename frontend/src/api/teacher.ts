import http from './http'
import type { Course, ClassSession, Homework, HomeworkSubmission, AttendanceRecord, CourseFile } from '@/types'

const base = (courseId: number) => `/api/teacher/courses/${courseId}`

export const teacherApi = {
  // 课程
  courses: () => http.get<Course[]>('/api/teacher/courses/'),
  createCourse: (data: object) => http.post<Course>('/api/teacher/courses/', data),
  courseDetail: (courseId: number) => http.get<Course>(`${base(courseId)}/`),
  updateCourse: (courseId: number, data: Partial<Course>) =>
    http.patch<Course>(`${base(courseId)}/`, data),

  // 课节
  classes: (courseId: number) => http.get<ClassSession[]>(`${base(courseId)}/classes/`),
  createClass: (courseId: number, data: object) =>
    http.post<ClassSession>(`${base(courseId)}/classes/`, data),
  classDetail: (courseId: number, classId: number) =>
    http.get<ClassSession>(`${base(courseId)}/classes/${classId}/`),
  updateClass: (courseId: number, classId: number, data: object) =>
    http.patch<ClassSession>(`${base(courseId)}/classes/${classId}/`, data),
  deleteClass: (courseId: number, classId: number) =>
    http.delete(`${base(courseId)}/classes/${classId}/`),

  // 课节资料文件（复用 admin 接口，staff 有权访问）
  uploadClassFile: (courseId: number, classId: number, file: File) => {
    const fd = new FormData(); fd.append('file', file)
    return http.post<CourseFile>(
      `/api/admin/courses/${courseId}/classes/${classId}/files/`, fd,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
  },
  deleteClassFile: (courseId: number, classId: number, fileId: number) =>
    http.delete(`/api/admin/courses/${courseId}/classes/${classId}/files/${fileId}/`),

  // 出勤
  attendance: (courseId: number, classId: number) =>
    http.get<AttendanceRecord[]>(`${base(courseId)}/classes/${classId}/attendance/`),
  updateAttendance: (courseId: number, classId: number, records: AttendanceRecord[]) =>
    http.put(`${base(courseId)}/classes/${classId}/attendance/`, records),

  // 作业
  homework: (courseId: number) => http.get<Homework[]>(`${base(courseId)}/homework/`),
  createHomework: (courseId: number, data: object) =>
    http.post<Homework>(`${base(courseId)}/homework/`, data),
  homeworkDetail: (courseId: number, homeworkId: number) =>
    http.get<Homework>(`${base(courseId)}/homework/${homeworkId}/`),
  updateHomework: (courseId: number, homeworkId: number, data: object) =>
    http.patch<Homework>(`${base(courseId)}/homework/${homeworkId}/`, data),
  deleteHomework: (courseId: number, homeworkId: number) =>
    http.delete(`${base(courseId)}/homework/${homeworkId}/`),

  // 提交 & 评分
  submissions: (courseId: number, homeworkId: number) =>
    http.get<HomeworkSubmission[]>(`${base(courseId)}/homework/${homeworkId}/submissions/`),
  grade: (courseId: number, homeworkId: number, submissionId: number, score: number) =>
    http.patch<HomeworkSubmission>(
      `${base(courseId)}/homework/${homeworkId}/submissions/${submissionId}/grade/`,
      { score },
    ),
}
