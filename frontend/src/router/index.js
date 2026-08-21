import { createRouter, createWebHistory } from 'vue-router'

import SectionPlaceholderPage from '@/views/pages/SectionPlaceholderPage.vue'
import LoginPage from '@/views/pages/LoginPage.vue'
import { useAuthStore } from '@/stores/authStore'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/main',
    },
    {
      path: '/login',
      name: 'login-page',
      component: LoginPage,
      meta: {
        title: '로그인',
        public: true,
        hideChrome: true,
      },
    },
    {
      path: '/main',
      name: 'main-page',
      component: SectionPlaceholderPage,
      meta: {
        title: '메인',
        description: '메인 화면은 추후 상세 기능을 추가할 예정입니다.',
      },
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (!to.meta.public && !authStore.isAuthenticated) {
    return { path: '/login' }
  }

  if (to.name === 'login-page' && authStore.isAuthenticated) {
    return { path: '/main' }
  }

  return true
})

export default router