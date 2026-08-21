<script setup>
import { computed, ref, useSlots, watch } from 'vue'

import Button from '@/components/atoms/Button.vue'
import Input from '@/components/atoms/Input.vue'
import ModalMessage from '@/components/atoms/modal/ModalMessage.vue'
import ModalFooter from '@/components/molecules/modal/ModalFooter.vue'
import ModalHeader from '@/components/molecules/modal/ModalHeader.vue'
import PromptField from '@/components/molecules/modal/PromptField.vue'
import BaseModal from '@/components/organisms/modal/BaseModal.vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '입력'
  },
  message: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  defaultValue: {
    type: String,
    default: ''
  },
  confirmText: {
    type: String,
    default: '확인'
  },
  cancelText: {
    type: String,
    default: '취소'
  },
  maxLength: {
    type: Number,
    default: undefined
  },
  validator: {
    type: Function,
    default: null
  },
  confirmDisabled: {
    type: Boolean,
    default: false
  },
  cardClass: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['confirm', 'cancel', 'close'])
const slots = useSlots()

const value = ref('')
const invalidMessage = ref('')
const hasCustomFields = computed(() => Boolean(slots.fields))

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) {
      return
    }

    value.value = props.defaultValue ?? ''
    invalidMessage.value = ''
  },
  { immediate: true }
)

const validateValue = () => {
  if (typeof props.validator !== 'function') {
    invalidMessage.value = ''
    return true
  }

  const nextMessage = props.validator(value.value)
  invalidMessage.value = typeof nextMessage === 'string' ? nextMessage : ''
  return !invalidMessage.value
}

const handleInput = (nextValue) => {
  if (typeof props.maxLength === 'number' && String(nextValue).length > props.maxLength) {
    value.value = String(nextValue).slice(0, props.maxLength)
    return
  }
  value.value = nextValue
  invalidMessage.value = ''
}

const handleConfirm = () => {
  if (hasCustomFields.value) {
    emit('confirm')
    return
  }

  if (!validateValue()) {
    return
  }

  emit('confirm', value.value)
}
</script>

<template>
  <BaseModal :open="open" :card-class="cardClass" @close="emit('close')">
    <ModalHeader title-id="prompt-dialog-title" :title="title" @close="emit('close')" />
    <ModalMessage>{{ message }}</ModalMessage>
    <slot v-if="hasCustomFields" name="fields" :confirm="handleConfirm" />
    <PromptField v-else :invalid-message="invalidMessage">
      <Input
        :model-value="value"
        :placeholder="placeholder"
        :invalid="Boolean(invalidMessage)"
        @update:model-value="handleInput"
        @enter="handleConfirm"
      />
    </PromptField>
    <ModalFooter>
      <Button size="sm" variant="secondary" @click="emit('cancel')">{{ cancelText }}</Button>
      <Button size="sm" :disabled="confirmDisabled" @click="handleConfirm">{{ confirmText }}</Button>
    </ModalFooter>
  </BaseModal>
</template>
