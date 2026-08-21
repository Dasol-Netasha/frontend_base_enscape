<script setup>
import Button from '@/components/atoms/Button.vue'
import ModalFooter from '@/components/molecules/modal/ModalFooter.vue'
import ModalHeader from '@/components/molecules/modal/ModalHeader.vue'
import BaseModal from '@/components/organisms/modal/BaseModal.vue'

defineProps({
  open: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '확인'
  },
  confirmText: {
    type: String,
    default: '확인'
  },
  cancelText: {
    type: String,
    default: '취소'
  }
})

const emit = defineEmits(['confirm', 'cancel', 'close'])
</script>

<template>
  <BaseModal :open="open" @close="emit('close')">
    <ModalHeader title-id="confirm-dialog-title" :title="title" @close="emit('close')" />
    <slot />
    <ModalFooter>
      <Button size="sm" variant="secondary" @click="emit('cancel')">{{ cancelText }}</Button>
      <Button size="sm" @click="emit('confirm')">{{ confirmText }}</Button>
    </ModalFooter>
  </BaseModal>
</template>
