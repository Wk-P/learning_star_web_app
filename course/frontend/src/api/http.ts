import axios, { type AxiosError } from 'axios'
import { useToast } from '@/composables/useToast'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
  timeout: 10_000,
})

// ── 请求拦截：注入 token + UTC 时间戳 ────────────────────────────────────────
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  config.headers['X-Client-UTC'] = new Date().toISOString()
  return config
})

// ── 响应拦截：token 刷新 + 统一错误 alert ────────────────────────────────────
const STATUS_MESSAGES: Record<number, string> = {
  400: '请求参数错误',
  401: '登录已过期，请重新登录',
  403: '权限不足',
  404: '资源不存在',
  409: '数据冲突，请刷新后重试',
  422: '数据校验失败',
  500: '服务器内部错误',
  502: '服务不可用，请稍后重试',
}

let isRefreshing = false
let pendingQueue: Array<(token: string) => void> = []

http.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const status = error.response?.status

    if (status === 401) {
      const refresh = localStorage.getItem('refresh_token')
      if (!refresh) {
        redirectToLogin()
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve) => {
          pendingQueue.push((token) => {
            error.config!.headers!.Authorization = `Bearer ${token}`
            resolve(http(error.config!))
          })
        })
      }

      isRefreshing = true
      try {
        const { data } = await axios.post(
          `${http.defaults.baseURL}/api/token/refresh/`,
          { refresh },
        )
        localStorage.setItem('access_token', data.access)
        if (data.refresh) localStorage.setItem('refresh_token', data.refresh)
        pendingQueue.forEach((cb) => cb(data.access))
        pendingQueue = []
        error.config!.headers!.Authorization = `Bearer ${data.access}`
        return http(error.config!)
      } catch {
        redirectToLogin()
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }

    const msg = status
      ? (STATUS_MESSAGES[status] ?? `请求失败 (${status})`)
      : '网络连接失败，请检查网络'

    useToast().error(msg)
    return Promise.reject(error)
  },
)

function redirectToLogin() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  const loginPath = `${import.meta.env.BASE_URL}login`
  if (window.location.pathname !== loginPath) {
    window.location.href = loginPath
  }
}

export default http
