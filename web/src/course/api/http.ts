import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { useToast } from '@/course/composables/useToast'
import { useAuthStore } from '@/core/stores/auth'
import { COURSE_API } from '@/core/api/endpoints'

const http = axios.create({
  baseURL: COURSE_API,
  timeout: 10_000,
})

// ── 请求拦截：注入统一登录的 token + UTC 时间戳 ──────────────────────────────
http.interceptors.request.use((config) => {
  const token = useAuthStore().accessToken
  if (token) config.headers.Authorization = `Bearer ${token}`
  config.headers['X-Client-UTC'] = new Date().toISOString()
  return config
})

// ── 响应拦截：401 时经 topik 刷新令牌后重试一次；其余错误统一提示 ──────────────
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

http.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const status = error.response?.status
    const config = error.config as (InternalAxiosRequestConfig & { _retried?: boolean }) | undefined

    if (status === 401 && config && !config._retried) {
      const auth = useAuthStore()
      if (await auth.refresh()) {
        config._retried = true
        return http(config)
      }
      auth.expire()
      return Promise.reject(error)
    }

    const msg = status
      ? (STATUS_MESSAGES[status] ?? `请求失败 (${status})`)
      : '网络连接失败，请检查网络'

    useToast().error(msg)
    return Promise.reject(error)
  },
)

export default http
