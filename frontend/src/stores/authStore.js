import { ref } from 'vue'
import { defineStore } from 'pinia'

const AUTH_KEY = 'auth:isAuthenticated'

export const useAuthStore = defineStore('auth', () => {
  const isAuthenticated = ref(sessionStorage.getItem(AUTH_KEY) === 'true')

  const login = (id, password) => {
    // TODO: 실제 백엔드 인증으로 교체하세요. 지금은 base 템플릿용 임시 계정입니다.
    if (id === 'admin' && password === 'admin') {
      isAuthenticated.value = true
      sessionStorage.setItem(AUTH_KEY, 'true')
      return true
    }
    return false
  }

  const logout = () => {
    isAuthenticated.value = false
    sessionStorage.removeItem(AUTH_KEY)
  }

  return {
    isAuthenticated,
    login,
    logout,
  }
})
