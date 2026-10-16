import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

function parseJwtPayload(token: string): Record<string, unknown> {
  try {
    const base64 = (token.split('.')[1] ?? '').replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(base64))
  } catch {
    return {}
  }
}

function setCookie(name: string, value: string) {
  document.cookie = `${name}=${value}; path=${import.meta.env.BASE_URL}; SameSite=Lax`
}

function clearCookie(name: string) {
  document.cookie = `${name}=; path=${import.meta.env.BASE_URL}; max-age=0`
}

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  const isLoggedIn = computed(() => !!accessToken.value)

  const isAdmin = computed(() => {
    if (!accessToken.value) return false
    return !!parseJwtPayload(accessToken.value)['is_staff']
  })

  const username = computed(() => {
    if (!accessToken.value) return ''
    return (parseJwtPayload(accessToken.value)['username'] as string) || ''
  })

  const userId = computed(() => {
    if (!accessToken.value) return null
    return (parseJwtPayload(accessToken.value)['user_id'] as number) ?? null
  })

  // sync cookie on startup so ProtectedMediaView can read it immediately
  if (accessToken.value) {
    setCookie('access_token', accessToken.value)
  }

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    setCookie('access_token', access)
  }

  function clearTokens() {
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    clearCookie('access_token')
  }

  return { accessToken, refreshToken, isLoggedIn, isAdmin, username, userId, setTokens, clearTokens }
})
