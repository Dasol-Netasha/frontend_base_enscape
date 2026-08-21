<script setup>
defineProps({
  direction: {
    type: String,
    default: 'none'
  }
})
</script>

<template>
  <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
    <path
      v-if="direction === 'desc'"
      d="M6 8L10 12L14 8"
      stroke="currentColor"
      stroke-width="1.8"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      v-else
      d="M6 12L10 8L14 12"
      stroke="currentColor"
      stroke-width="1.8"
      stroke-linecap="round"
      stroke-linejoin="round"
      :opacity="direction === 'none' ? 0.45 : 1"
    />
  </svg>
</template>
