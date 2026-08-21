<script setup>
defineProps({
  id: {
    type: String,
    default: ''
  }
})
</script>

<template>
  <h2 :id="id" class="text-base font-semibold text-slate-900">
    <slot />
  </h2>
</template>
