<script setup>
import IconButton from '@/components/atoms/IconButton.vue'
import SortIcon from '@/components/atoms/icons/SortIcon.vue'

const props = defineProps({
  direction: {
    type: String,
    default: 'none'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  ariaLabel: {
    type: String,
    default: '정렬'
  }
})

const emit = defineEmits(['click'])
</script>

<template>
  <IconButton
    class="sort-icon-btn"
    variant="ghost"
    size="sm"
    :disabled="disabled"
    flat
    :aria-label="ariaLabel"
    @click="emit('click', $event)"
  >
    <SortIcon :direction="direction" />
  </IconButton>
</template>

<style scoped>
:deep(.sort-icon-btn.btn-base) {
  border: none !important;
  box-shadow: none !important;
  --tw-ring-shadow: 0 0 #0000 !important;
  --tw-shadow: 0 0 #0000 !important;
  -webkit-tap-highlight-color: transparent;
}

:deep(.sort-icon-btn.btn-base:hover),
:deep(.sort-icon-btn.btn-base:focus),
:deep(.sort-icon-btn.btn-base:focus-visible),
:deep(.sort-icon-btn.btn-base:active) {
  outline: none !important;
  box-shadow: none !important;
  border-color: transparent !important;
  --tw-ring-shadow: 0 0 #0000 !important;
  --tw-shadow: 0 0 #0000 !important;
}
</style>
