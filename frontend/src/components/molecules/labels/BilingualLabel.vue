<script setup>
import { computed } from 'vue'

import Tooltip from '@/components/atoms/Tooltip.vue'
import { parseBilingualLabel } from '@/utils/bilingualLabel'

const props = defineProps({
  label: {
    type: String,
    default: '',
  },
  textClass: {
    type: String,
    default: '',
  },
  showTooltip: {
    type: Boolean,
    default: true,
  },
})

const parsed = computed(() => parseBilingualLabel(props.label))
</script>

<template>
  <Tooltip :content="props.showTooltip ? parsed.tooltip : ''">
    <span :class="textClass">{{ parsed.display }}</span>
  </Tooltip>
</template>
