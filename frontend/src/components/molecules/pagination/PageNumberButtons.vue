<script setup>
import { computed } from 'vue'

const props = defineProps({
  page: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['go-page'])

const pageItems = computed(() => {
  if (props.totalPages <= 9) {
    return Array.from({ length: props.totalPages }, (_, index) => index + 1)
  }

  const start = Math.max(2, props.page - 3)
  const end = Math.min(props.totalPages - 1, props.page + 3)
  const items = [1]

  if (start > 2) {
    items.push('ellipsis-left')
  }

  for (let page = start; page <= end; page += 1) {
    items.push(page)
  }

  if (end < props.totalPages - 1) {
    items.push('ellipsis-right')
  }

  items.push(props.totalPages)
  return items
})
</script>

<template>
  <template v-for="item in pageItems" :key="`page-item-${item}`">
    <span v-if="typeof item === 'string'" class="px-1 text-sm text-slate-400">...</span>
    <button
      v-else
      type="button"
      class="h-8 min-w-8 rounded border px-2 text-sm"
      :class="item === page ? 'border-slate-900 bg-slate-900 text-white' : 'border-slate-300 text-slate-700 hover:bg-slate-50'"
      :disabled="disabled || item === page"
      @click="emit('go-page', item)"
    >
      {{ item }}
    </button>
  </template>
</template>
