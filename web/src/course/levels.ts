import type { VideoLevel } from '@/course/types'

export interface LevelMeta {
  key: VideoLevel
  step: number
  hint: string
  color: string
}

// 入门 → 基础 → 进阶：一条视频可属于多个阶段
export const LEVELS: LevelMeta[] = [
  { key: '入门', step: 1, hint: '零基础起步，建立整体认识', color: '#16a34a' },
  { key: '基础', step: 2, hint: '系统学习核心知识点', color: '#2563eb' },
  { key: '进阶', step: 3, hint: '专题深入与综合提升', color: '#9333ea' },
]

// B 站按 BV 号（+分P）查重，其余链接忽略协议与查询参数；与后端 video_key 保持一致
export function videoKey(url: string) {
  const bv = url.match(/BV[0-9A-Za-z]{10}/)?.[0]
  if (bv) {
    const p = url.match(/[?&]p=(\d+)/)?.[1]
    return `${bv}#${p && p !== '1' ? p : ''}`
  }
  return url.split(/[?#]/)[0]!.replace(/^https?:\/\//, '').replace(/\/+$/, '').toLowerCase()
}
