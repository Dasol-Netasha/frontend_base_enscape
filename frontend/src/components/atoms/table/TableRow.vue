<script setup>
const props = defineProps({
  hover: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <tr class="table-row" :class="{ 'table-row-hover': hover }">
    <slot />
  </tr>
</template>
