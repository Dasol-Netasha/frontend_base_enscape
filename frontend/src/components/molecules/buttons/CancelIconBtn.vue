<script setup>
import IconButton from '@/components/atoms/IconButton.vue'
import CloseIcon from '@/components/atoms/icons/CloseIcon.vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'ghost'
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
    default: '취소'
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
    <CloseIcon />
  </IconButton>
</template>
