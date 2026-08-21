<script setup>
const props = defineProps({
  type: {
    type: String,
    required: true,
    validator: (value) => ['first', 'prev', 'next', 'last'].includes(value)
  }
})
</script>

<template>
  <span aria-hidden="true" class="font-mono text-sm leading-none">
    <template v-if="type === 'first'">&lt;&lt;</template>
    <template v-else-if="type === 'prev'">&lt;</template>
    <template v-else-if="type === 'next'">&gt;</template>
    <template v-else>&gt;&gt;</template>
  </span>
</template>
