<script setup>
defineProps({
  eyebrow: {
    type: String,
    default: '',
  },
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <section class="space-y-6">
    <header class="rounded-[28px] border border-white/60 bg-white/85 px-6 py-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] backdrop-blur sm:px-8">
      <p v-if="eyebrow" class="text-xs font-semibold uppercase tracking-[0.28em] text-sky-700">{{ eyebrow }}</p>
      <h2 class="mt-2 font-['Pretendard','SUIT','Noto_Sans_KR',sans-serif] text-2xl font-semibold tracking-[-0.04em] text-slate-950 sm:text-3xl">{{ title }}</h2>
      <p v-if="description" class="mt-3 max-w-3xl text-sm leading-6 text-slate-600 sm:text-base">{{ description }}</p>
    </header>
    <slot />
  </section>
</template>
