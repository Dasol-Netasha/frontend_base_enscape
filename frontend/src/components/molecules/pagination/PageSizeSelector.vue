<script setup>
import { computed } from 'vue'

import Button from '@/components/atoms/Button.vue'
import DropdownMenu from '@/components/molecules/dropdown/DropdownMenu.vue'
import Dropdown from '@/components/organisms/dropdown/Dropdown.vue'

const props = defineProps({
  modelValue: {
    type: Number,
    required: true
  },
  options: {
    type: Array,
    default: () => [10, 20, 30, 40, 50]
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const dropdownItems = computed(() => {
  return props.options.map((option) => ({
    key: option,
    label: `${option}개`
  }))
})

const handleSelect = (item, close) => {
  emit('update:modelValue', Number(item.key))
  close()
}
</script>

<template>
  <Dropdown align="start">
    <template #trigger="{ isOpen, toggle, panelId }">
      <Button
        variant="secondary"
        size="sm"
        :disabled="disabled"
        :aria-expanded="isOpen"
        :aria-controls="panelId"
        @click="toggle"
      >
        {{ modelValue }}
      </Button>
    </template>

    <template #default="{ close }">
      <DropdownMenu
        :items="dropdownItems"
        :active-key="modelValue"
        @select="handleSelect($event, close)"
      />
    </template>
  </Dropdown>
</template>
