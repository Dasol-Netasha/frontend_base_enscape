<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const title = computed(() => String(route.meta?.title || '준비 중'))
const description = computed(() => String(route.meta?.description || '해당 화면은 순차적으로 구성될 예정입니다.'))
</script>

<template>
  <section class="rounded-2xl border border-white/70 bg-white/80 p-8 shadow-[0_20px_60px_rgba(15,23,42,0.06)] backdrop-blur">
    <h1 class="text-2xl font-semibold text-slate-900">{{ title }}</h1>
    <p class="mt-3 text-sm text-slate-600">{{ description }}</p>
  </section>
</template>
