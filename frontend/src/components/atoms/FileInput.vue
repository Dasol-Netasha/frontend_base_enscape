<script setup>
import { computed } from 'vue'

const props = defineProps({
  accept: {
    type: String,
    default: '.csv,.xlsx'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'md'
  }
})

const emit = defineEmits(['change'])

const sizeClass = computed(() => {
  const sizes = {
    sm: 'input-sm',
    md: 'input-md',
    lg: 'input-lg'
  }

  return sizes[props.size] ?? sizes.md
})

const handleChange = (event) => {
  const file = event.target.files?.[0] ?? null
  emit('change', file)
}
</script>

<template>
  <input
    type="file"
    class="input-base"
    :class="[sizeClass]"
    :accept="accept"
    :disabled="disabled"
    @change="handleChange"
  />
</template>
