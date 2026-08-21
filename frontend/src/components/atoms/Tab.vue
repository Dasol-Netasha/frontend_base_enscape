<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  active: {
    type: Boolean,
    default: false
  },
  line: {
    type: Boolean,
    default: false
  },
  orientation: {
    type: String,
    default: 'horizontal'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  extraClass: {
    type: [String, Array, Object],
    default: ''
  }
})

const emit = defineEmits(['select'])

const stateClass = computed(() => {
  if (!props.line) {
    return props.active ? 'tab-item-active' : 'tab-item-inactive'
  }

  if (!props.active) {
    return 'tab-item-line-inactive'
  }

  return props.orientation === 'vertical'
    ? 'tab-item-line-active-vertical'
    : 'tab-item-line-active-horizontal'
})

const handleClick = () => {
  if (!props.disabled) {
    emit('select', props.value)
  }
}
</script>

<template>
  <button
    type="button"
    role="tab"
    class="tab-item"
    :class="[stateClass, extraClass]"
    :disabled="disabled"
    :aria-selected="active"
    @click="handleClick"
  >
    {{ label }}
  </button>
</template>
