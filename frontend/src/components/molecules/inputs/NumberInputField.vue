<script setup>
import { computed } from 'vue'

import Input from '@/components/atoms/Input.vue'
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
    <Input
      :model-value="modelValue ?? ''"
      type="number"
      :placeholder="placeholder || `${parsedLabel.display} 입력`"
      size="sm"
      @update:model-value="emit('update:modelValue', $event)"
    />
  </div>
</template>
