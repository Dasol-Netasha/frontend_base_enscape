
<script setup>
import { ref } from 'vue'
const props = defineProps({
  role: {
    type: String,
    default: 'dialog'
  },
  ariaModal: {
    type: String,
    default: 'true'
  }
})
const rootEl = ref(null)
defineExpose({ rootEl })
</script>

<template>
  <section
    ref="rootEl"
    :role="role"
    :aria-modal="ariaModal"
    :class="['relative w-full rounded-xl border border-slate-200 bg-white p-5 shadow-xl', cardClass]"
  >
    <slot />
  </section>
</template>
