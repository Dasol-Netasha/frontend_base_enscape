<script setup>
import { computed } from 'vue'
import Tab from '@/components/atoms/Tab.vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  items: {
    type: Array,
    default: () => []
  },
  orientation: {
    type: String,
    default: 'horizontal'
  },
  line: {
    type: Boolean,
    default: false
  },
  lineFrame: {
    type: Boolean,
    default: true
  },
  align: {
    type: String,
    default: 'left',
    validator: (value) => ['left', 'center', 'right'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue'])

const handleSelect = (value) => {
  emit('update:modelValue', value)
}

const normalizedOrientation = computed(() => {
  return props.orientation === 'vertical' ? 'vertical' : 'horizontal'
})

const listClass = computed(() => {
  const orientationClass = normalizedOrientation.value === 'vertical' ? 'tab-list-vertical' : 'tab-list-horizontal'
  const modeClass = props.line ? 'tab-list-line' : 'tab-list-solid'
  const modeOrientationClass = props.line && props.lineFrame
    ? (normalizedOrientation.value === 'vertical' ? 'tab-list-line-vertical' : 'tab-list-line-horizontal')
    : ''

  const alignClass = normalizedOrientation.value === 'horizontal'
    ? (props.align === 'center' ? 'tab-list-align-center' : props.align === 'right' ? 'tab-list-align-right' : 'tab-list-align-left')
    : ''

  return [orientationClass, modeClass, modeOrientationClass, alignClass]
})

const itemClass = computed(() => {
  const orientationClass = normalizedOrientation.value === 'vertical' ? 'tab-item-vertical' : 'tab-item-horizontal'
  const modeClass = props.line ? 'tab-item-line' : 'tab-item-solid'

  return [orientationClass, modeClass]
})
</script>

<template>
  <div class="tab-list" :class="listClass" role="tablist" :aria-orientation="normalizedOrientation">
    <Tab
      v-for="item in items"
      :key="item.value"
      :label="item.label"
      :value="item.value"
      :active="item.value === modelValue"
      :disabled="Boolean(item.disabled)"
      :line="line"
      :orientation="normalizedOrientation"
      :extra-class="itemClass"
      @select="handleSelect"
    />
  </div>
</template>
