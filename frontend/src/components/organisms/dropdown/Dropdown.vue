<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  align: {
    type: String,
    default: 'end',
    validator: (value) => ['start', 'end'].includes(value)
  }
})

const isOpen = ref(false)
const rootRef = ref(null)
const panelId = `dropdown-panel-${Math.random().toString(36).slice(2, 10)}`

const contentClass = computed(() => {
  return props.align === 'start' ? 'dropdown-content dropdown-content-start' : 'dropdown-content dropdown-content-end'
})

const open = () => {
  isOpen.value = true
}

const close = () => {
  isOpen.value = false
}

const toggle = () => {
  isOpen.value = !isOpen.value
}

const handleOutsideClick = (event) => {
  if (!rootRef.value || rootRef.value.contains(event.target)) {
    return
  }

  close()
}

const handleEscape = (event) => {
  if (event.key === 'Escape') {
    close()
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleOutsideClick)
  document.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleOutsideClick)
  document.removeEventListener('keydown', handleEscape)
})
</script>

<template>
  <div ref="rootRef" class="dropdown-root">
    <slot
      name="trigger"
      :is-open="isOpen"
      :toggle="toggle"
      :open="open"
      :close="close"
      :panel-id="panelId"
    />

    <div v-if="isOpen" :id="panelId" :class="contentClass">
      <slot :close="close" />
    </div>
  </div>
</template>
