<script setup>
defineProps({
  content: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <span class="group relative inline-flex items-center align-middle">
    <slot />
    <span
      v-if="content"
      role="tooltip"
      class="pointer-events-none absolute bottom-full left-1/2 z-30 mb-1 hidden min-w-32 max-w-80 -translate-x-1/2 whitespace-normal break-words rounded-md bg-slate-900 px-2 py-1 text-[11px] font-medium text-white shadow-lg group-hover:block group-focus-within:block"
    >
      {{ content }}
    </span>
  </span>
</template>
