/**
 * 视频链接解析：识别平台、提取视频 ID，用于显示、查重与打开链接。
 * 规则与后端 course_views.py 的 parse_video_link 保持一致；新增平台两边各加一条。
 */

export type Platform = 'bilibili' | 'youtube' | 'other'

export interface PlatformMeta {
  /** 显示名，同时也是后端自动打上的平台标签 */
  label: string
  color: string
}

export const PLATFORMS: Record<Platform, PlatformMeta> = {
  bilibili: { label: 'B站', color: '#fb7299' },
  youtube: { label: 'YouTube', color: '#ff0033' },
  other: { label: '链接', color: '#64748b' },
}

export interface VideoLink {
  platform: Platform
  /** B 站为 BV 号，YouTube 为 11 位视频 ID；识别不出为空 */
  id: string
  /** B 站分P（>1 时才有） */
  part?: number
  host: string
}

const BILI_HOST = /(^|\.)(bilibili\.com|b23\.tv|bili2233\.cn)$/
const YT_HOST = /(^|\.)(youtube\.com|youtu\.be|youtube-nocookie\.com)$/

function toUrl(raw: string): URL | null {
  try {
    return new URL(raw.trim().replace(/^http:\/\//i, 'https://'))
  } catch {
    return null
  }
}

export function parseVideoLink(raw: string): VideoLink {
  const u = toUrl(raw)
  const host = u?.hostname.toLowerCase() ?? ''

  if (BILI_HOST.test(host)) {
    const id = raw.match(/BV[0-9A-Za-z]{10}/)?.[0] ?? ''
    const p = Number(u!.searchParams.get('p'))
    return { platform: 'bilibili', id, host, ...(p > 1 ? { part: p } : {}) }
  }
  if (YT_HOST.test(host)) {
    const id =
      (host.endsWith('youtu.be') ? u!.pathname.slice(1, 12) : '') ||
      u!.searchParams.get('v') ||
      u!.pathname.match(/^\/(?:shorts|embed|live|v)\/([\w-]{11})/)?.[1] ||
      ''
    return { platform: 'youtube', id: /^[\w-]{11}$/.test(id) ? id : '', host }
  }
  return { platform: 'other', id: '', host }
}

/** 查重键：能识别出视频 ID 的按「平台:ID」（同一 BV 的不同分P也算重复），否则按去掉协议与参数的链接 */
export function videoKey(raw: string) {
  const { platform, id } = parseVideoLink(raw)
  if (id) return `${platform}:${id}`
  return raw.trim().split(/[?#]/)[0]!.replace(/^https?:\/\//i, '').replace(/\/+$/, '').toLowerCase()
}

/** 列表里显示的短文本：BV 号（· P2）/ YouTube ID / 域名 */
export function shortLink(raw: string) {
  const l = parseVideoLink(raw)
  if (l.id) return l.part ? `${l.id} · P${l.part}` : l.id
  return l.host.replace(/^www\./, '') || raw
}

/**
 * 打开用的链接：统一 https；B 站去掉 spm_id_from / vd_source 等追踪参数（只保留分P）——
 * 来自陌生站点的 Referer 与追踪参数容易触发 B 站风控返回 412。YouTube 只保留 v / t / list。
 */
export function cleanUrl(raw: string) {
  const u = toUrl(raw)
  if (!u) return raw.trim()
  const { platform, part } = parseVideoLink(raw)
  if (platform === 'bilibili') {
    u.search = part ? `?p=${part}` : ''
    u.hash = ''
  } else if (platform === 'youtube') {
    const keep = new URLSearchParams()
    for (const k of ['v', 't', 'list']) {
      const val = u.searchParams.get(k)
      if (val) keep.set(k, val)
    }
    u.search = keep.toString() ? `?${keep}` : ''
  }
  return u.href
}

/**
 * 从粘贴的文本里拆出链接和标题，兼容：
 *   纯链接 / 「标题 链接」/ B 站 App 分享的「【标题】 链接」/ 链接在前、说明在后
 */
export function parsePaste(text: string): { url: string; title: string } {
  const m = text.match(/https?:\/\/[^\s　，。、】」）]+/i)
  if (!m) return { url: '', title: '' }
  const url = m[0]
  const before = text.slice(0, m.index).trim()
  const after = text.slice(m.index! + url.length).trim()
  return { url, title: (before || after).replace(/\s+/g, ' ') }
}
