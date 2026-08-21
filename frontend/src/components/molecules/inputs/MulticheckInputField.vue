<script setup>
import Checkbox from '@/components/atoms/Checkbox.vue'
import BilingualLabel from '@/components/molecules/labels/BilingualLabel.vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  modelValue: {
    type: Array,
    default: () => []
  },
  options: {
    type: Array,
    default: () => []
  },
  required: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const isSelected = (value) => Array.isArray(props.modelValue) && props.modelValue.includes(value)

const toggleOption = (value) => {
  const current = Array.isArray(props.modelValue) ? [...props.modelValue] : []
  const index = current.indexOf(value)
  if (index >= 0) {
    current.splice(index, 1)
  } else {
    current.push(value)
  }
  emit('update:modelValue', current.length > 0 ? current : null)
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <label class="text-xs font-medium text-slate-600">
      <BilingualLabel :label="props.label" />
      <span v-if="props.required" class="ml-0.5 text-rose-500">*</span>
    </label>
    <div class="space-y-1.5">
      <div v-for="opt in props.options" :key="opt.value" class="flex items-center gap-2">
        <Checkbox
          :model-value="isSelected(opt.value)"
          @update:model-value="toggleOption(opt.value)"
        />
        <label class="text-xs text-slate-600">{{ opt.label }}</label>
      </div>
    </div>
  </div>
</template>
