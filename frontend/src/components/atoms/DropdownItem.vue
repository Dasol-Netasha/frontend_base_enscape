<script setup>
import BilingualLabel from '@/components/molecules/labels/BilingualLabel.vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  danger: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  active: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select'])

const handleSelect = () => {
  if (!props.disabled) {
    emit('select')
  }
}
</script>

<template>
  <button
    type="button"
    class="dropdown-item"
    :class="{
      'dropdown-item-danger': danger,
      'dropdown-item-disabled': disabled,
      'dropdown-item-active': active
    }"
    :disabled="disabled"
    @click="handleSelect"
  >
    <span class="dropdown-item-icon">
      <slot name="icon" />
    </span>
    <BilingualLabel :label="label" />
  </button>
</template>
