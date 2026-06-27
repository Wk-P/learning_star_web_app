export type UserRole = 'user' | 'admin'

export interface User {
  id: number
  userId: string
  username: string
  email: string
  role: UserRole
  displayName: string
}

export interface Subject {
  id: number
  name: string
  description: string
  icon: string
  color: string
  courseCount: number
}

export interface Course {
  id: number
  subjectId: number | null
  subjectName: string
  name: string
  description: string
}

export interface BilibiliVideo {
  index: number
  title: string
  url: string
}

export interface TokenPair {
  access: string
  refresh: string
}

export interface LoginPayload {
  username: string
  password: string
}

export interface AdminUserDetail extends User {
  dateJoined: string
  isActive: boolean
  userId: string
}
