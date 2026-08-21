<script setup>
import { computed } from 'vue'

const props = defineProps({
  align: {
    type: String,
    default: 'left'
  }
})

const alignClass = computed(() => {
  if (props.align === 'center') return 'table-cell-center'
  if (props.align === 'right') return 'table-cell-right'
  return 'table-cell-left'
})
</script>

<template>
  <td class="table-td" :class="alignClass">
    <slot />
  </td>
</template>
