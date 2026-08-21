<script setup>
import BilingualLabel from '@/components/molecules/labels/BilingualLabel.vue'

const props = defineProps({
  label: {
    type: String,
    default: ''
  },
  invalidMessage: {
    type: String,
    default: ''
  },
  scrollable: {
    type: Boolean,
    default: true
  },
  maxHeightClass: {
    type: String,
    default: 'max-h-72'
  }
})
</script>

<template>
  <div class="mt-3 space-y-1">
    <p v-if="label" class="text-xs font-semibold text-slate-600">
      <BilingualLabel :label="label" />
    </p>
    <div
      :class="[
        'space-y-2',
        props.scrollable ? [props.maxHeightClass, 'overflow-y-auto pr-1'] : '',
      ]"
    >
      <slot />
    </div>
    <p v-if="invalidMessage" class="text-xs text-rose-600">{{ invalidMessage }}</p>
  </div>
</template>
