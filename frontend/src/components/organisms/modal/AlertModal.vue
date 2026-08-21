<script setup>
import Button from '@/components/atoms/Button.vue'
import ModalMessage from '@/components/atoms/modal/ModalMessage.vue'
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
    default: '알림'
  },
  message: {
    type: String,
    default: ''
  },
  confirmText: {
    type: String,
    default: '확인'
  }
})

const emit = defineEmits(['confirm', 'close'])
</script>

<template>
  <BaseModal :open="open" @close="emit('close')">
    <ModalHeader title-id="alert-dialog-title" :title="title" @close="emit('close')" />
    <ModalMessage>{{ message }}</ModalMessage>
    <ModalFooter>
      <Button size="sm" @click="emit('confirm')">{{ confirmText }}</Button>
    </ModalFooter>
  </BaseModal>
</template>
