<script setup>
const props = defineProps({
  activeValue: {
    type: [String, Number],
    required: true
  },
  panelValue: {
    type: [String, Number],
    required: true
  }
})
</script>

<template>
  <section v-show="activeValue === panelValue" class="tab-panel" role="tabpanel">
    <slot />
  </section>
</template>
