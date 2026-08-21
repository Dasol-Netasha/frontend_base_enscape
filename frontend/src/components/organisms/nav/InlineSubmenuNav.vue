<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Tab from '@/components/atoms/Tab.vue'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  align: {
    type: String,
    default: 'center',
    validator: (value) => ['left', 'center', 'right'].includes(value)
  }
})

const route = useRoute()
const router = useRouter()
const activeTab = ref('')

const normalizedItems = computed(() => {
  return props.items.map((item, index) => ({
    ...item,
    value: item.value ?? item.to ?? `${item.label}-${index}`,
    subItems: Array.isArray(item.subItems) ? item.subItems : []
  }))
})

const isRouteMatched = (targetPath) => {
  if (!targetPath) {
    return false
  }

  return route.path === targetPath || route.path.startsWith(`${targetPath}/`)
}

const syncActiveTab = () => {
  const routeMatchedItem = normalizedItems.value.find((item) => isRouteMatched(item.to))
  activeTab.value = routeMatchedItem?.value || normalizedItems.value[0]?.value || ''
}

watch(() => props.items, syncActiveTab, { immediate: true, deep: true })
watch(() => route.path, syncActiveTab)

const activeItem = computed(() => {
  return normalizedItems.value.find((item) => item.value === activeTab.value) || null
})

const activeSubItems = computed(() => activeItem.value?.subItems || [])

const handleChange = (value) => {
  activeTab.value = value

  const selectedItem = normalizedItems.value.find((item) => item.value === value)
  if (!selectedItem?.to || selectedItem.to === route.path) {
    return
  }

  router.push(selectedItem.to)
}

const alignClass = computed(() => {
  if (props.align === 'left') {
    return 'tab-list-align-left'
  }

  if (props.align === 'right') {
    return 'tab-list-align-right'
  }

  return 'tab-list-align-center'
})
</script>

<template>
  <nav v-if="normalizedItems.length" class="tabs-layout tabs-layout-horizontal" aria-label="Local navigation">
    <div class="tab-list tab-list-horizontal tab-list-line tab-list-line-horizontal" :class="alignClass" role="tablist" aria-orientation="horizontal">
      <Tab
        v-for="item in normalizedItems"
        :key="item.value"
        :label="item.label"
        :value="item.value"
        :active="item.value === activeTab"
        :line="true"
        orientation="horizontal"
        :extra-class="['tab-item-horizontal', 'tab-item-line']"
        @select="handleChange"
      />
    </div>

    <div
      class="flex min-h-6 flex-wrap items-center gap-x-4 gap-y-1 pt-1"
      :class="alignClass"
    >
      <RouterLink
        v-for="subItem in activeSubItems"
        :key="subItem.id ?? subItem.value ?? subItem.path"
        :to="subItem.path ?? subItem.to"
        class="px-1 text-xs transition-colors"
        :class="isRouteMatched(subItem.path ?? subItem.to) ? 'font-semibold text-[var(--theme-text-strong)]' : 'text-[var(--theme-text-subtle)] hover:text-[var(--theme-text-strong)]'"
      >
        {{ subItem.name ?? subItem.label }}
      </RouterLink>
    </div>
  </nav>
</template>