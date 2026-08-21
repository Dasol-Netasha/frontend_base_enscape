<script setup>
import Input from '@/components/atoms/Input.vue'
import BilingualLabel from '@/components/molecules/labels/BilingualLabel.vue'

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  modelValue: {
    type: String,
    default: '',
  },
  required: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="flex flex-col gap-1">
    <label class="text-xs font-medium text-slate-600">
      <BilingualLabel :label="props.label" />
      <span v-if="props.required" class="ml-0.5 text-rose-500">*</span>
    </label>
    <Input
      :model-value="props.modelValue ?? ''"
      type="date"
      size="sm"
      @update:model-value="emit('update:modelValue', $event)"
    />
  </div>
</template>