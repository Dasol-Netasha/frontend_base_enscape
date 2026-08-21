<script setup>
import ModalMessage from '@/components/atoms/modal/ModalMessage.vue'
import AlertModal from '@/components/organisms/modal/AlertModal.vue'
import ConfirmModal from '@/components/organisms/modal/ConfirmModal.vue'
import PromptModal from '@/components/organisms/modal/PromptModal.vue'

defineProps({
  dialog: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['alert-confirm', 'confirm-accept', 'confirm-cancel', 'prompt-submit', 'prompt-cancel'])
</script>

<template>
  <AlertModal
    v-if="dialog?.type === 'alert'"
    :open="true"
    :title="dialog.options.title ?? '알림'"
    :message="dialog.options.message ?? ''"
    :confirm-text="dialog.options.confirmText ?? '확인'"
    @confirm="emit('alert-confirm')"
    @close="emit('alert-confirm')"
  />

  <ConfirmModal
    v-else-if="dialog?.type === 'confirm'"
    :open="true"
    :title="dialog.options.title ?? '확인'"
    :confirm-text="dialog.options.confirmText ?? '확인'"
    :cancel-text="dialog.options.cancelText ?? '취소'"
    @confirm="emit('confirm-accept')"
    @cancel="emit('confirm-cancel')"
    @close="emit('confirm-cancel')"
  >
    <ModalMessage v-if="dialog.options.message">{{ dialog.options.message }}</ModalMessage>
  </ConfirmModal>

  <PromptModal
    v-else-if="dialog?.type === 'prompt'"
    :open="true"
    :title="dialog.options.title ?? '입력'"
    :message="dialog.options.message ?? ''"
    :placeholder="dialog.options.placeholder ?? ''"
    :default-value="dialog.options.defaultValue ?? ''"
    :confirm-text="dialog.options.confirmText ?? '확인'"
    :cancel-text="dialog.options.cancelText ?? '취소'"
    :max-length="dialog.options.maxLength"
    :validator="dialog.options.validator"
    @confirm="(value) => emit('prompt-submit', value)"
    @cancel="emit('prompt-cancel')"
    @close="emit('prompt-cancel')"
  />
</template>
