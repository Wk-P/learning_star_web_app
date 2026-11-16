/** 语言学习的最近学习记录（只存在本机浏览器） */
const KEY = 'huntu_history'
const MAX = 20

export interface HistoryItem {
  /** 语言 slug，如 ko */
  lang: string
  type: 'video' | 'audio' | 'file'
  title: string
  url: string
  path: string[]
  ts: number
}

// 合并前的记录没有 lang，媒体地址是 /media/videos|audios|pdfs/...（当时只有韩语）
const LEGACY_URL = /^\/media\/(videos|audios|pdfs)\//
const LEGACY_DIR: Record<string, string> = { videos: 'videos', audios: 'audios', pdfs: 'files' }

function upgrade(h: HistoryItem): HistoryItem {
  if (h.lang) return h
  const url = h.url.replace(LEGACY_URL, (_, d: string) => `/media/languages/ko/${LEGACY_DIR[d]}/`)
  return { ...h, lang: 'ko', url }
}

function load(): HistoryItem[] {
  try {
    const raw = JSON.parse(localStorage.getItem(KEY) || '[]')
    return Array.isArray(raw) ? raw.map(upgrade) : []
  } catch {
    return []
  }
}

function save(items: HistoryItem[]) {
  try { localStorage.setItem(KEY, JSON.stringify(items)) } catch { /* 隐私模式等 */ }
}

export function addHistory(item: Omit<HistoryItem, 'ts'>) {
  const list = load().filter((h) => h.url !== item.url)
  list.unshift({ ...item, ts: Date.now() })
  save(list.slice(0, MAX))
}

/** 不传 lang 返回全部语言的记录 */
export function getHistory(lang?: string): HistoryItem[] {
  const all = load()
  return lang ? all.filter((h) => h.lang === lang) : all
}
