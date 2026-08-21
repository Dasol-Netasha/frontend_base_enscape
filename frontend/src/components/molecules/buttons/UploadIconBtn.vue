<script setup>
import IconButton from '@/components/atoms/IconButton.vue'
import UploadIcon from '@/components/atoms/icons/UploadIcon.vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary'
  },
  size: {
    type: String,
    default: 'md'
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
    default: false
  },
  ariaLabel: {
    type: String,
    default: '업로드'
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
    <UploadIcon />
  </IconButton>
</template>
