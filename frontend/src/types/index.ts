// ── 用户角色 ──────────────────────────────────────────────────────────────────
export type UserRole = 'user' | 'staff' | 'admin'

export interface User {
  id: number
  userId: string   // 8位hex，如 a1b2c3d4
  username: string
  email: string
  role: UserRole
  displayName: string
}

// ── 科目 ──────────────────────────────────────────────────────────────────────
export interface Subject {
  id: number
  name: string
  description: string
  icon: string
  color: string
  courseCount: number
}

// ── 课程状态 ──────────────────────────────────────────────────────────────────
export type CourseStatus = 'not_started' | 'in_progress' | 'ended'

export interface Course {
  id: number
  subjectId: number | null
  subjectName: string
  teacherId: number | null
  teacherName: string
  name: string
  description: string
  schedule: string     // 如：每周二 09:00-11:00
  status: CourseStatus
  startTime: string    // ISO 8601
  endTime: string
  durationWeeks: number
}

// ── 课节 ──────────────────────────────────────────────────────────────────────
export interface CourseFile {
  id: number
  name: string
  url: string
}

export interface ClassSession {
  id: number
  courseId: number
  week: number
  session: number
  title: string          // 例：第n周第m课
  classTime: string      // ISO 8601
  meetingUrl: string
  memo: string
  status: 'normal' | 'cancelled'
  teacherId: number | null
  teacherName: string
  students: string[]     // username list
  files: CourseFile[]
}

// ── 作业 ──────────────────────────────────────────────────────────────────────
export type HomeworkStatus = 'not_started' | 'in_progress' | 'ended'

export interface Homework {
  id: number
  courseId: number
  courseName: string
  name: string
  description: string
  startTime: string
  endTime: string
  maxScore: number
  status: HomeworkStatus
}

// ── 作业提交 ──────────────────────────────────────────────────────────────────
export interface HomeworkSubmission {
  id: number
  homeworkId: number
  userId: number
  submittedAt: string
  fileUrl: string
  fileName: string
  score: number | null
  graded: boolean
}

// ── 用户-课程关联 ─────────────────────────────────────────────────────────────
export interface EnrollmentRecord {
  courseId: number
  courseName: string
  enrolledAt: string
  courseStatus: CourseStatus
}

// ── 成绩 ──────────────────────────────────────────────────────────────────────
export interface CourseScore {
  courseId: number
  courseName: string
  courseStatus: CourseStatus
  finalScore: number | null
  graded: boolean
}

// ── API 响应通用结构 ──────────────────────────────────────────────────────────
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// ── 登录 ──────────────────────────────────────────────────────────────────────
export interface TokenPair {
  access: string
  refresh: string
}

export interface LoginPayload {
  username: string
  password: string
}

// ── Admin 专用 ────────────────────────────────────────────────────────────────
export interface AdminUserDetail extends User {
  dateJoined: string
  isActive: boolean
  userId: string
}

export interface AttendanceRecord {
  classId: number
  userId: number
  present: boolean
  note: string
}
