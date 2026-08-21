<script setup>
import InlineSubmenuNav from '@/components/organisms/nav/InlineSubmenuNav.vue'

defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  align: {
    type: String,
    default: 'center',
    validator: (value) => ['left', 'center', 'right'].includes(value),
  },
})
</script>

<template>
  <div v-if="items.length" class="pt-1">
    <InlineSubmenuNav :items="items" :align="align" />
  </div>
</template>
