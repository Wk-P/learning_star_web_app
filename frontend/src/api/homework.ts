import http from './http'
import type { Homework, HomeworkSubmission } from '@/types'

export const homeworkApi = {
  // 获取某课程下的作业列表
  listByCourse: (courseId: number) =>
    http.get<Homework[]>(`/api/courses/${courseId}/homework/`),

  // 获取当前用户所有作业（含当周 + 历史）
  myList: () => http.get<Homework[]>('/api/homework/my-list/'),

  // 获取单个作业详情
  get: (homeworkId: number) => http.get<Homework>(`/api/homework/${homeworkId}/`),

  // 获取当前用户对某作业的提交记录
  mySubmission: (homeworkId: number) =>
    http.get<HomeworkSubmission>(`/api/homework/${homeworkId}/my-submission/`),

  // 提交作业（multipart/form-data）
  submit: (homeworkId: number, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return http.post<HomeworkSubmission>(`/api/homework/${homeworkId}/submit/`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}
