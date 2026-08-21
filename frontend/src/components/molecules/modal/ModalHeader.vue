<script setup>
import ModalCloseBtn from '@/components/atoms/modal/ModalCloseBtn.vue'
import ModalTitle from '@/components/atoms/modal/ModalTitle.vue'

defineProps({
  title: {
    type: String,
    default: ''
  },
  titleId: {
    type: String,
    default: ''
  },
  closable: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close'])
</script>

<template>
  <header class="flex items-start justify-between gap-3">
    <ModalTitle :id="titleId">{{ title }}</ModalTitle>
    <ModalCloseBtn v-if="closable" @click="emit('close')" />
  </header>
</template>
