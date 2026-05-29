import http from './http'
import type { ClassSession } from '@/types'

export const classApi = {
  // 获取某课程下所有课节
  listByCourse: (courseId: number) =>
    http.get<ClassSession[]>(`/api/courses/${courseId}/classes/`),

  // 获取单个课节详情
  get: (courseId: number, classId: number) =>
    http.get<ClassSession>(`/api/courses/${courseId}/classes/${classId}/`),
}
