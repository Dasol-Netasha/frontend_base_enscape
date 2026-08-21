<script setup>
defineProps({
  total: {
    type: Number,
    required: true
  }
})
</script>

<template>
  <span class="text-sm text-slate-600">{{ total }}</span>
</template>
