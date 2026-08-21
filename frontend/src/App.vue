<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { useUiModeStore } from '@/stores/uiModeStore'
import { useThemeStore } from '@/stores/themeStore'
import { useAuthStore } from '@/stores/authStore'
import Header from '@/components/organisms/Header.vue'

const route = useRoute()
const router = useRouter()
const uiModeStore = useUiModeStore()
const themeStore = useThemeStore()
const authStore = useAuthStore()
const appThemeClass = computed(() => `theme-${themeStore.theme}`)
const showChrome = computed(() => !route.meta?.hideChrome)

// 대시보드전용 사이트는 이 배열을 비워두면 GlobalNav가 렌더링되지 않습니다.
const mainMenuItems = []

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
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
    <Header v-if="showChrome" :menu-items="mainMenuItems" @logout="handleLogout" @options="handleOptions" />

    <div v-if="showChrome" class="mx-auto flex w-full max-w-[1600px] flex-1 flex-col px-4 py-4 sm:px-6 lg:px-8">
      <main class="flex-1 py-6">
        <RouterView />
      </main>
    </div>
    <RouterView v-else />
  </div>
</template>
