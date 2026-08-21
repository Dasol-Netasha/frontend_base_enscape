<script setup>
const emit = defineEmits(['click'])
</script>

<template>
  <div
    class="absolute inset-0 bg-black/40"
    aria-hidden="true"
    @click="emit('click')"
  />
</template>
