/** 站点名称与栏目定义（改名只需改这里） */
export const BRAND = 'Learning Star'
export const BRAND_TAGLINE = '韩语与课程学习平台'

export type SectionKey = 'topik' | 'course'

export interface Section {
  key: SectionKey
  label: string
  short: string
  desc: string
  icon: 'audio' | 'book'
  color: string
  to: string
  /** 栏目内二级导航 */
  tabs: Array<{ label: string; to: string; exact?: boolean }>
}

export const SECTIONS: Record<SectionKey, Section> = {
  topik: {
    key: 'topik',
    label: '韩语 TOPIK',
    short: '韩语',
    desc: '视频课程、听力音频与学习资料',
    icon: 'audio',
    color: '#2ec4c0',
    to: '/topik',
    tabs: [
      { label: '概览', to: '/topik', exact: true },
      { label: '视频', to: '/topik/video' },
      { label: '音频', to: '/topik/audio' },
      { label: '资料', to: '/topik/file' },
    ],
  },
  course: {
    key: 'course',
    label: '课程',
    short: '课程',
    desc: '数学、英语、计算机等科目的精选 B 站课程',
    icon: 'book',
    color: '#1e4fa8',
    to: '/course',
    tabs: [
      { label: '科目视频', to: '/course', exact: true },
      { label: '学习路线图', to: '/course/roadmap' },
      { label: '思维导图', to: '/course/mindmap' },
    ],
  },
}
