<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  emptyText: {
    type: String,
    default: '-'
  },
  clickable: {
    type: Boolean,
    default: false
  },
  disableLast: {
    type: Boolean,
    default: true
  }
})

const router = useRouter()

const canNavigate = (item, index) => {
  if (!props.clickable) {
    return false
  }

  if (!item?.to) {
    return false
  }

  if (props.disableLast && index === props.items.length - 1) {
    return false
  }

  return true
}

const handleClick = (item, index) => {
  if (!canNavigate(item, index)) {
    return
  }

  router.push(item.to)
}
</script>

<template>
  <p class="mt-2 text-xs text-slate-600">
    <template v-if="items.length > 0">
      <span
        v-for="(item, index) in items"
        :key="item.key || `${item.label}-${index}`"
      >
        <span v-if="index > 0" class="mx-1 text-slate-400">/</span>
        <button
          v-if="canNavigate(item, index)"
          type="button"
          class="text-slate-700 underline-offset-2 hover:text-slate-900 hover:underline"
          @click="handleClick(item, index)"
        >
          {{ item.label }}
        </button>
        <span v-else>{{ item.label }}</span>
      </span>
    </template>
    <span v-else>{{ emptyText }}</span>
  </p>
</template>
