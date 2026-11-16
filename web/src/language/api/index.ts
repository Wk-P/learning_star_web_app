import { request, json } from '@/core/api/http'

/** 资源类型：视频 / 音频 / 资料（资料可以是 pdf、xlsx、hwp 等，只提供下载） */
export type MediaKind = 'video' | 'audio' | 'file'

export const MEDIA_KINDS: { key: MediaKind; label: string; icon: 'video' | 'audio' | 'file' }[] = [
  { key: 'video', label: '视频', icon: 'video' },
  { key: 'audio', label: '音频', icon: 'audio' },
  { key: 'file', label: '资料', icon: 'file' },
]

export interface Language {
  id: number
  category: number
  name: string
  /** 网址与媒体目录用的标识，如 ko */
  slug: string
  native_name: string
  description: string
  color: string
  sort_order: number
  is_active: boolean
}

export interface LanguageCategory {
  id: number
  name: string
  description: string
  sort_order: number
  languages: Language[]
}

export interface MediaItem {
  id: number
  title: string
  url: string
  /** 扩展名：m3u8 / mp3 / pdf / xlsx / hwp … */
  ext: string
}

export interface MediaFolder {
  id: number
  path: string[]
  items: MediaItem[]
}

export const languageApi = {
  categories() {
    return request<LanguageCategory[]>('/languages/')
  },
  media(slug: string, kind: MediaKind) {
    return request<MediaFolder[]>(`/languages/${encodeURIComponent(slug)}/${kind}/`)
  },

  // ── 管理员：分类与语言 ──
  createCategory(data: Partial<LanguageCategory>) {
    return request<LanguageCategory>('/languages/admin/categories/', json('POST', data))
  },
  updateCategory(id: number, data: Partial<LanguageCategory>) {
    return request<LanguageCategory>(`/languages/admin/categories/${id}/`, json('PATCH', data))
  },
  deleteCategory(id: number) {
    return request<void>(`/languages/admin/categories/${id}/`, json('DELETE'))
  },
  createLanguage(data: Partial<Language>) {
    return request<Language>('/languages/admin/languages/', json('POST', data))
  },
  updateLanguage(id: number, data: Partial<Language>) {
    return request<Language>(`/languages/admin/languages/${id}/`, json('PATCH', data))
  },
  deleteLanguage(id: number) {
    return request<void>(`/languages/admin/languages/${id}/`, json('DELETE'))
  },
}


/** 从文件地址取扩展名（小写，不含点） */
export function fileExt(url: string): string {
  const name = url.split('?')[0]?.split('/').pop() ?? ''
  const dot = name.lastIndexOf('.')
  return dot > 0 ? name.slice(dot + 1).toLowerCase() : ''
}
