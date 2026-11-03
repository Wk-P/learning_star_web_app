import type { VideoLevel } from '@/course/types'

export interface LevelMeta {
  key: VideoLevel
  step: number
  hint: string
  color: string
}

// 入门 → 基础 → 进阶：每个视频只属于一个阶段（levels 至多一项）
export const LEVELS: LevelMeta[] = [
  { key: '入门', step: 1, hint: '零基础起步，建立整体认识', color: '#16a34a' },
  { key: '基础', step: 2, hint: '系统学习核心知识点', color: '#2563eb' },
  { key: '进阶', step: 3, hint: '专题深入与综合提升', color: '#9333ea' },
]

