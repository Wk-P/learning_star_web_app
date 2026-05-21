import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(localStorage.getItem('theme') !== 'light')

  function applyTheme() {
    const theme = isDark.value ? 'dark' : 'light'
    document.documentElement.setAttribute('data-theme', theme)
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
