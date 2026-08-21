<script setup>
import { nextTick, onUnmounted, ref, watch } from 'vue'

import ModalBackdrop from '@/components/atoms/modal/ModalBackdrop.vue'
import ModalCard from '@/components/atoms/modal/ModalCard.vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  cardClass: {
    type: String,
    default: ''
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true
  },
  closeOnEsc: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close'])

const cardRef = ref(null)
let previousActiveElement = null

const focusModal = async () => {
  await nextTick()
  const root = cardRef.value?.rootEl || cardRef.value
  if (!root) {
    return
  }

  const focusTarget = root.querySelector('input, textarea, select, button, [tabindex]:not([tabindex="-1"])')
  if (focusTarget) {
    focusTarget.focus()
    return
  }

  root.focus()
}

const handleEsc = (event) => {
  if (!props.open || !props.closeOnEsc) {
    return
  }
  if (event.key === 'Escape') {
    emit('close')
  }
}

const lockBodyScroll = () => {
  document.body.style.overflow = 'hidden'
}

const restoreBodyScroll = () => {
  document.body.style.overflow = ''
}

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      previousActiveElement = document.activeElement
      lockBodyScroll()
      await focusModal()
      return
    }

    restoreBodyScroll()
    if (previousActiveElement && typeof previousActiveElement.focus === 'function') {
      previousActiveElement.focus()
    }
  }
)

onUnmounted(() => {
  restoreBodyScroll()
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[100] flex items-center justify-center p-4"
      @keydown.esc="handleEsc"
    >
      <ModalBackdrop @click="closeOnBackdrop ? emit('close') : null" />
      <ModalCard ref="cardRef" tabindex="-1" :class="cardClass">
        <slot />
      </ModalCard>
    </div>
  </Teleport>
</template>
