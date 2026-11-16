/**
 * public/ 下静态资源的 URL。站点若部署在子路径下（vite base），
 * 模板里写死的 "/img/x.webp" 会丢掉前缀，统一经过这里拼接 base。
 *   asset('img/logo-96.webp')  →  BASE_URL + 'img/logo-96.webp'
 */
export function asset(path: string): string {
  return import.meta.env.BASE_URL + path.replace(/^\//, '')
}

/** 同一张图的多个宽度版本 → srcset 字符串 */
export function srcset(entries: Array<[path: string, width: number]>): string {
  return entries.map(([p, w]) => `${asset(p)} ${w}w`).join(', ')
}
