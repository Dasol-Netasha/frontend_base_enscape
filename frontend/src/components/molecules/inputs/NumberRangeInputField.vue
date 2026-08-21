<script setup>
import Input from '@/components/atoms/Input.vue'
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
  required: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const updateMin = (value, currentMax) => {
  emit('update:modelValue', [Number(value) || '', currentMax ?? ''])
}

const updateMax = (currentMin, value) => {
  emit('update:modelValue', [currentMin ?? '', Number(value) || ''])
}
</script>

<template>
  <div class="flex flex-col gap-1">
    <label class="text-xs font-medium text-slate-600">
      <BilingualLabel :label="props.label" />
      <span v-if="props.required" class="ml-0.5 text-rose-500">*</span>
    </label>
    <div class="flex gap-1">
      <Input
        :model-value="props.modelValue?.[0] ?? ''"
        type="number"
        placeholder="최소"
        size="sm"
        @update:model-value="updateMin($event, props.modelValue?.[1])"
      />
      <Input
        :model-value="props.modelValue?.[1] ?? ''"
        type="number"
        placeholder="최대"
        size="sm"
        @update:model-value="updateMax(props.modelValue?.[0], $event)"
      />
    </div>
  </div>
</template>
