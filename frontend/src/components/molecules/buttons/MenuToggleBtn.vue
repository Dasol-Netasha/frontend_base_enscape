<script setup>
import IconButton from '@/components/atoms/IconButton.vue'

const props = defineProps({
  size: {
    type: String,
    default: 'sm'
  },
  variant: {
    type: String,
    default: 'ghost'
  },
  outlined: {
    type: Boolean,
    default: false
  },
  flat: {
    type: Boolean,
    default: false
  },
  ariaLabel: {
    type: String,
    default: 'Open menu'
  }
})

const emit = defineEmits(['click'])
</script>

<template>
  <IconButton
    :size="size"
    :variant="variant"
    :outlined="outlined"
    :flat="flat"
    :aria-label="ariaLabel"
    @click="emit('click', $event)"
  >
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <path d="M3 6h18" />
      <path d="M3 12h18" />
      <path d="M3 18h18" />
    </svg>
  </IconButton>
</template>
