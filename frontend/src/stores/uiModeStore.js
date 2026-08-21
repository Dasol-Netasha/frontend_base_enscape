import { defineStore } from 'pinia'
import { ref } from 'vue'

const HACK_MODE_KEY = 'ui:hack-mode'

export const useUiModeStore = defineStore('uiMode', () => {
  const isHackMode = ref(localStorage.getItem(HACK_MODE_KEY) === 'true')

  const setHackMode = (value) => {
    isHackMode.value = Boolean(value)
    localStorage.setItem(HACK_MODE_KEY, String(isHackMode.value))
  }

  const toggleHackMode = () => {
    setHackMode(!isHackMode.value)
  }

  return {
    isHackMode,
    setHackMode,
    toggleHackMode,
  }
})
