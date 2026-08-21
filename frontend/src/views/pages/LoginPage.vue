<script setup>
import { computed } from 'vue'
import LoginForm from '@/views/organisms/login-page/LoginForm.vue'
import { useThemeStore } from '@/stores/themeStore'
import logoBlue from '@/assets/images/logos/logo_blue.png'
import logoWhite from '@/assets/images/logos/logo_white.png'

const themeStore = useThemeStore()
const logoSrc = computed(() => (themeStore.isDark ? logoWhite : logoBlue))
</script>

<template>
  <div class="flex min-h-screen flex-col items-center justify-center gap-6 theme-shell-bg theme-text-primary">
    <img :src="logoSrc" alt="Logo" class="h-10 w-auto" />
    <LoginForm />
  </div>
</template>
