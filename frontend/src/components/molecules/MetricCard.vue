<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    required: true,
  },
  hint: {
    type: String,
    default: '',
  },
  accent: {
    type: String,
    default: 'from-sky-500/20 to-cyan-500/10',
  },
})
</script>

<template>
  <article class="relative overflow-hidden rounded-[24px] border border-slate-200 bg-white p-5 shadow-[0_14px_40px_rgba(15,23,42,0.06)]">
    <div class="absolute inset-x-0 top-0 h-1 bg-gradient-to-r" :class="accent" />
    <p class="text-sm font-medium text-slate-500">{{ label }}</p>
    <p class="mt-3 text-3xl font-semibold tracking-[-0.04em] text-slate-950">{{ value }}</p>
    <p v-if="hint" class="mt-2 text-sm text-slate-500">{{ hint }}</p>
  </article>
</template>
