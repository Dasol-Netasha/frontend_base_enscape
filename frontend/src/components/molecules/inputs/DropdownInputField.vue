<script setup>
import { computed } from 'vue'

import Select from '@/components/atoms/Select.vue'
import BilingualLabel from '@/components/molecules/labels/BilingualLabel.vue'
import { parseBilingualLabel } from '@/utils/bilingualLabel'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  modelValue: {
    type: [String, Number],
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  },
  placeholder: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])
const parsedLabel = computed(() => parseBilingualLabel(props.label))
</script>

<template>
  <div class="flex flex-col gap-1">
    <label class="text-xs font-medium text-slate-600">
      <BilingualLabel :label="label" />
      <span v-if="required" class="ml-0.5 text-rose-500">*</span>
    </label>
    <Select
      :model-value="modelValue ?? ''"
      :options="options"
      size="sm"
      :placeholder="placeholder || `${parsedLabel.display} 선택`"
      @update:model-value="emit('update:modelValue', $event)"
    />
  </div>
</template>
