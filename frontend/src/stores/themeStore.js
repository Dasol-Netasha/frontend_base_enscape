import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

const THEME_KEY = 'ui:theme'
const THEME_LIGHT = 'light'
const THEME_DARK = 'dark'

const resolveInitialTheme = () => {
  const saved = localStorage.getItem(THEME_KEY)
  if (saved === THEME_LIGHT || saved === THEME_DARK) {
    return saved
  }

  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)')?.matches
  return prefersDark ? THEME_DARK : THEME_LIGHT
}

const applyThemeClass = (theme) => {
  const root = document.documentElement
  root.classList.remove('theme-light', 'theme-dark')
  root.classList.add(theme === THEME_DARK ? 'theme-dark' : 'theme-light')
}

export const useThemeStore = defineStore('theme', () => {
  const theme = ref(THEME_LIGHT)
  const isDark = computed(() => theme.value === THEME_DARK)

  const setTheme = (nextTheme) => {
    theme.value = nextTheme === THEME_DARK ? THEME_DARK : THEME_LIGHT
    localStorage.setItem(THEME_KEY, theme.value)
    applyThemeClass(theme.value)
  }

  const toggleTheme = () => {
    setTheme(isDark.value ? THEME_LIGHT : THEME_DARK)
  }

  const initializeTheme = () => {
    setTheme(resolveInitialTheme())
  }

  return {
    theme,
    isDark,
    setTheme,
    toggleTheme,
    initializeTheme,
  }
})
