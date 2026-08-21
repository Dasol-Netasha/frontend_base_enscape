<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { RouterView } from 'vue-router'
import { useUiModeStore } from '@/stores/uiModeStore'
import { useThemeStore } from '@/stores/themeStore'
import Header from '@/components/organisms/Header.vue'

const uiModeStore = useUiModeStore()
const themeStore = useThemeStore()
const appThemeClass = computed(() => `theme-${themeStore.theme}`)

// 대시보드전용 사이트는 이 배열을 비워두면 GlobalNav가 렌더링되지 않습니다.
const mainMenuItems = []

const handleLogout = () => {
  // TODO: 프로젝트별 로그아웃 로직을 연결하세요.
}

const handleOptions = () => {
  // TODO: 프로젝트별 옵션 화면을 연결하세요.
}

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
    class="app-shell flex min-h-screen flex-col theme-shell-bg theme-text-primary"
    :class="appThemeClass"
    :data-hack-mode="uiModeStore.isHackMode ? 'on' : 'off'"
  >
    <Header :menu-items="mainMenuItems" @logout="handleLogout" @options="handleOptions" />

    <div class="mx-auto flex w-full max-w-[1600px] flex-1 flex-col px-4 py-4 sm:px-6 lg:px-8">
      <main class="flex-1 py-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
