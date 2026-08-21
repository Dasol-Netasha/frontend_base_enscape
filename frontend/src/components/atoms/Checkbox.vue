<script setup>
import { computed, onMounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  indeterminate: {
    type: Boolean,
    default: false,
  },
  ariaLabel: {
    type: String,
    default: 'checkbox',
  },
})

const emit = defineEmits(['update:modelValue', 'change'])
const inputRef = ref(null)

const inputClass = computed(() => {
  return ['checkbox-base', props.disabled ? 'checkbox-disabled' : '']
})

const syncIndeterminate = () => {
  if (inputRef.value) {
    inputRef.value.indeterminate = props.indeterminate
  }
}

const handleChange = (event) => {
  const checked = event.target.checked
  emit('update:modelValue', checked)
  emit('change', checked)
}

onMounted(syncIndeterminate)
watch(() => props.indeterminate, syncIndeterminate)
</script>

<template>
  <input
    ref="inputRef"
    type="checkbox"
    :checked="modelValue"
    :disabled="disabled"
    :aria-label="ariaLabel"
    :class="inputClass"
    @change="handleChange"
  />
</template>
