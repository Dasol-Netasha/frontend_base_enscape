<script setup>
import BreadcrumbTrail from '@/components/molecules/navigation/BreadcrumbTrail.vue'

defineProps({
  breadcrumbItems: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: ''
  }
})
</script>

<template>
  <header>
    <BreadcrumbTrail :items="breadcrumbItems" clickable class="mb-2" />
    <h2 class="text-lg font-semibold text-slate-900">{{ title || '선택된 메뉴 없음' }}</h2>
  </header>
</template>
