<script setup>
import IconButton from '@/components/atoms/IconButton.vue'
import DownloadIcon from '@/components/atoms/icons/DownloadIcon.vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'ghost'
  },
  size: {
    type: String,
    default: 'sm'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  rounded: {
    type: Boolean,
    default: true
  },
  outlined: {
    type: Boolean,
    default: false
  },
  flat: {
    type: Boolean,
    default: true
  },
  ariaLabel: {
    type: String,
    default: '다운로드'
  }
})

const emit = defineEmits(['click'])
</script>

<template>
  <IconButton
    :variant="variant"
    :size="size"
    :disabled="disabled"
    :rounded="rounded"
    :outlined="outlined"
    :flat="flat"
    :aria-label="ariaLabel"
    @click="emit('click', $event)"
  >
    <DownloadIcon />
  </IconButton>
</template>
