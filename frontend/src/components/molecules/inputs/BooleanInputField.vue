<script setup>
import Switch from '@/components/atoms/Switch.vue'
import BilingualLabel from '@/components/molecules/labels/BilingualLabel.vue'

defineProps({
  label: {
    type: String,
    required: true
  },
  modelValue: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div class="flex flex-col gap-1">
    <label class="text-xs font-medium text-slate-600">
      <BilingualLabel :label="label" />
      <span v-if="required" class="ml-0.5 text-rose-500">*</span>
    </label>
    <!-- <div class="flex items-center justify-between gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5"> -->
      <Switch
        :model-value="modelValue === true"
        @update:model-value="emit('update:modelValue', $event ? true : null)"
      />
    <!-- </div> -->
  </div>
</template>
