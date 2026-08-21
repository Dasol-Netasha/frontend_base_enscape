<script setup>
import { computed } from 'vue'
import GlobalNav from '@/views/organisms/GlobalNav.vue'
import HeaderOptionsMenu from '@/components/organisms/nav/HeaderOptionsMenu.vue'
import { useThemeStore } from '@/stores/themeStore'
import logoBlue from '@/assets/images/logos/logo_blue.png'
import logoWhite from '@/assets/images/logos/logo_white.png'

defineProps({
  // 대시보드전용 사이트는 빈 배열을 넘기면 GlobalNav가 렌더링되지 않습니다.
  menuItems: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['logout', 'options'])

const themeStore = useThemeStore()
const logoSrc = computed(() => (themeStore.isDark ? logoWhite : logoBlue))
</script>

<template>
  <header class="app-header">
    <div class="mx-auto flex w-full max-w-[1600px] items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
      <img :src="logoSrc" alt="Logo" class="h-8 w-auto shrink-0" />
      <div class="min-w-0 flex-1">
        <GlobalNav :items="menuItems" />
      </div>
      <HeaderOptionsMenu @logout="emit('logout')" @options="emit('options')" />
    </div>
  </header>
</template>
