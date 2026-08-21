<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { RouterView } from 'vue-router'
import { useUiModeStore } from '@/stores/uiModeStore'
import { useThemeStore } from '@/stores/themeStore'
import GlobalNav from '@/views/organisms/GlobalNav.vue'

const uiModeStore = useUiModeStore()
const themeStore = useThemeStore()
const appThemeClass = computed(() => `theme-${themeStore.theme}`)

const onGlobalKeydown = (event) => {
  if (event.altKey && event.shiftKey && event.key.toLowerCase() === 'q') {
    event.preventDefault()
    uiModeStore.toggleHackMode()
  }
}

onMounted(() => {
  themeStore.initializeTheme()
  window.addEventListener('keydown', onGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onGlobalKeydown)
})
</script>

<template>
  <div
    class="app-shell min-h-screen theme-shell-bg theme-text-primary"
    :class="appThemeClass"
    :data-hack-mode="uiModeStore.isHackMode ? 'on' : 'off'"
  >
    <div class="mx-auto flex min-h-screen w-full max-w-[1600px] flex-col px-4 py-4 sm:px-6 lg:px-8">
      <header class="app-header overflow-hidden rounded-[28px] px-6 pt-3 pb-1">
        <GlobalNav />
      </header>

      <main class="flex-1 py-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
