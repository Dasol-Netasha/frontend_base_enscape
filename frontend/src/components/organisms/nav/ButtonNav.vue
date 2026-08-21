<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
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

const route = useRoute()
const router = useRouter()

const normalizedItems = computed(() => {
  return props.items.map((item, index) => ({
    ...item,
    value: item.value ?? item.to ?? `${item.label}-${index}`,
  }))
})

const alignClass = computed(() => {
  if (props.align === 'left') {
    return 'justify-start'
  }
  if (props.align === 'right') {
    return 'justify-end'
  }
  return 'justify-center'
})

const isRouteMatched = (targetPath) => {
  if (!targetPath) {
    return false
  }

  return route.path === targetPath || route.path.startsWith(`${targetPath}/`)
}

const handleClick = (item) => {
  if (!item?.to || item.to === route.path) {
    return
  }
  router.push(item.to)
}
</script>

<template>
  <nav class="flex flex-wrap items-center gap-2" :class="alignClass">
    <button
      v-for="item in normalizedItems"
      :key="item.value"
      type="button"
      class="nav-pill"
      :class="isRouteMatched(item.to)
        ? 'nav-pill-active'
        : 'nav-pill-inactive'"
      @click="handleClick(item)"
    >
      {{ item.label }}
    </button>
  </nav>
</template>
