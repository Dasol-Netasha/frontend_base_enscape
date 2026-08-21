import { createRouter, createWebHistory } from 'vue-router'

import SectionPlaceholderPage from '@/views/pages/SectionPlaceholderPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/main',
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

export default router