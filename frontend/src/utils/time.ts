/**
 * 时间工具函数——全部基于浏览器本地时区。
 *
 * 服务器返回带时区偏移的 ISO 字符串（如 "2025-09-01T09:00:00+08:00"）。
 * new Date(iso) 会自动解析并转换为本地时区，
 * 因此所有函数都通过 new Date() 中转，确保跨时区正确。
 */

const pad = (n: number) => String(n).padStart(2, '0')

/** ISO → "YYYY-MM-DDTHH:mm"，用于 <input type="datetime-local"> 的 value */
export function toDatetimeLocal(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
}

/** ISO → "YYYY-MM-DD"，用于 <input type="date"> 的 value */
export function toDateLocal(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

/**
 * "YYYY-MM-DD" 日期字符串补全为当天 00:00:00 的 UTC ISO。
 * 前端 <input type="date"> 的 value 用此函数转换后提交给后端。
 */
export function dateToISOStart(date: string): string {
  if (!date) return ''
  // new Date(`${date}T00:00:00`) 解析为本地时间，toISOString() 转 UTC
  return new Date(`${date}T00:00:00`).toISOString()
}

/**
 * "YYYY-MM-DD" 日期字符串补全为当天 23:59:59 的 UTC ISO。
 */
export function dateToISOEnd(date: string): string {
  if (!date) return ''
  return new Date(`${date}T23:59:59`).toISOString()
}

/**
 * "YYYY-MM-DDTHH:mm"（datetime-local 的 value）→ UTC ISO。
 * 前端 <input type="datetime-local"> 的 value 用此函数转换后提交给后端。
 * 这样不管用户在哪个时区，后端收到的都是正确的 UTC 时间。
 */
export function datetimeLocalToISO(local: string): string {
  if (!local) return ''
  // "2025-09-01T09:00" → new Date 解析为本地时间 → .toISOString() → UTC
  return new Date(local).toISOString()
}

/** 显示用：本地时间，精确到分钟，例如 "2025-09-01 09:00" */
export function fmt(iso: string): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('zh-CN', {
    hour12: false,
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  }).replace(/\//g, '-')
}

/** 显示用：仅日期，例如 "2025/09/01" → "2025-09-01" */
export function fmtDate(iso: string): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
  }).replace(/\//g, '-')
}
