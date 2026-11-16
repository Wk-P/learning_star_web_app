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
  /** B 站搜索关键词，逗号分隔 */
  keywords: string
}

export type VideoLevel = '入门' | '基础' | '进阶'

export interface BilibiliVideo {
  /** 数据库 id：修改、删除用它 */
  id: number
  /** 在本科目列表中的位置（从 0 开始，前端补上，用于显示序号） */
  index: number
  title: string
  url: string
  levels: VideoLevel[]
  /** 自定义标签，可为空 */
  tags: string[]
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
