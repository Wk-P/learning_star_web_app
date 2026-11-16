import { useAuthStore } from '@/core/stores/auth'
import { API } from '@/core/api/endpoints'

/**
 * fetch 封装：自动带登录令牌；401 时刷新一次令牌后重试，仍失败则回到登录页。
 * 失败时抛出 Response，可用 errorDetail(e) 取后端返回的提示。
 */
export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const auth = useAuthStore()
  const makeHeaders = () => ({
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
    ...(auth.accessToken ? { Authorization: `Bearer ${auth.accessToken}` } : {}),
  })

  let res = await fetch(`${API}${path}`, { ...options, headers: makeHeaders() })

  if (res.status === 401 && auth.refreshToken) {
    if (await auth.refresh()) {
      res = await fetch(`${API}${path}`, { ...options, headers: makeHeaders() })
    } else {
      auth.expire()
      throw res
    }
  }

  if (!res.ok) throw res
  // 204 等无响应体的成功请求（如删除）直接返回
  const text = await res.text()
  return (text ? JSON.parse(text) : undefined) as T
}

export const json = (method: string, body?: unknown): RequestInit => ({
  method,
  body: body === undefined ? undefined : JSON.stringify(body),
})

/** 从失败的请求里取后端返回的提示文案（detail 或第一个字段错误） */
export async function errorDetail(e: unknown, fallback = '操作失败'): Promise<string> {
  if (e instanceof Response) {
    try {
      const data = await e.clone().json()
      if (typeof data?.detail === 'string') return data.detail
      const first = data && typeof data === 'object' ? Object.values(data)[0] : null
      if (Array.isArray(first) && typeof first[0] === 'string') return first[0]
    } catch { /* 非 JSON */ }
  }
  return fallback
}
