import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(localStorage.getItem('theme') !== 'light')

  function applyTheme() {
    const theme = isDark.value ? 'dark' : 'light'
    const root = document.documentElement
    root.setAttribute('data-theme', theme)
    // Element Plus 深色变量挂在 html.dark 上
    root.classList.toggle('dark', isDark.value)
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', isDark.value ? '#0a1428' : '#e6f5f4')
    localStorage.setItem('theme', theme)
  }

  function toggle() {
    isDark.value = !isDark.value
    applyTheme()
  }

  // apply on store creation (ensures sync with localStorage)
  applyTheme()

  return { isDark, toggle }
})
