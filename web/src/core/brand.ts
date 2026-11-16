/** 站点名称与栏目定义（改名只需改这里） */
export const BRAND = 'Learning Star'
export const BRAND_CN = '学习之星'
export const BRAND_TAGLINE = '语言与课程学习平台'

export type SectionKey = 'language' | 'course'

export interface SectionTab {
  label: string
  /** 可含 :lang，进入具体语言后替换为语言 slug；不在具体语言内时这类标签不显示 */
  to: string
  exact?: boolean
}

export interface Section {
  key: SectionKey
  label: string
  short: string
  desc: string
  icon: 'audio' | 'book'
  color: string
  to: string
  /** 栏目内二级导航 */
  tabs: SectionTab[]
}

export const SECTIONS: Record<SectionKey, Section> = {
  language: {
    key: 'language',
    label: '语言学习',
    short: '语言',
    desc: '按语言分类的视频课程、听力音频与学习资料',
    icon: 'audio',
    color: '#2ec4c0',
    to: '/language',
    tabs: [
      { label: '全部语言', to: '/language', exact: true },
      { label: '概览', to: '/language/:lang', exact: true },
      { label: '视频', to: '/language/:lang/video' },
      { label: '音频', to: '/language/:lang/audio' },
      { label: '资料', to: '/language/:lang/file' },
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
      { label: '学习路线', to: '/course/path' },
    ],
  },
}
