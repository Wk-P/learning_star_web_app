const KEY = 'huntu_history'
const MAX = 20

export interface HistoryItem {
  type: 'video' | 'audio' | 'file'
  title: string
  url: string
  path: string[]
  ts: number
}

function load(): HistoryItem[] {
  try { return JSON.parse(localStorage.getItem(KEY) || '[]') } catch { return [] }
}

function save(items: HistoryItem[]) {
  localStorage.setItem(KEY, JSON.stringify(items))
}

export function addHistory(item: Omit<HistoryItem, 'ts'>) {
  const list = load().filter(h => h.url !== item.url)
  list.unshift({ ...item, ts: Date.now() })
  save(list.slice(0, MAX))
}

export function getHistory(): HistoryItem[] {
  return load()
}
