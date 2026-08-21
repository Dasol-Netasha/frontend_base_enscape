<script setup>
import IconButton from '@/components/atoms/IconButton.vue'
import CloseIcon from '@/components/atoms/icons/CloseIcon.vue'

const emit = defineEmits(['click'])
</script>

<template>
  <IconButton
    size="sm"
    variant="ghost"
    rounded
    flat
    aria-label="닫기"
    @click="emit('click')"
  >
    <CloseIcon />
  </IconButton>
</template>
