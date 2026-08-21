<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SubNav from '@/components/organisms/nav/SubNav.vue'
import TabPanel from '@/components/molecules/TabPanel.vue'
import Tabs from '@/components/molecules/Tabs.vue'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  modelValue: {
    type: [String, Number],
    default: ''
  },
  defaultTab: {
    type: [String, Number],
    default: ''
  },
  line: {
    type: Boolean,
    default: false
  },
  divider: {
    type: Boolean,
    default: false
  },
  fill: {
    type: Boolean,
    default: true
  },
  showPanels: {
    type: Boolean,
    default: false
  },
  routeMode: {
    type: Boolean,
    default: true
  },
  submenu: {
    type: Boolean,
    default: false
  },
  submenuMaxDepth: {
    type: Number,
    default: Number.MAX_SAFE_INTEGER
  }
})

const emit = defineEmits(['update:modelValue'])

const activeTab = ref('')
const router = useRouter()
const route = useRoute()

const normalizedItems = computed(() => {
  return props.items.map((item, index) => ({
    ...item,
    value: item.value ?? item.to ?? `${item.label}-${index}`
  }))
})

const findItemByValue = (value) => normalizedItems.value.find((item) => item.value === value)
const activePanelItem = computed(() => findItemByValue(activeTab.value) ?? null)

const findNestedItemByValue = (value, nodes = normalizedItems.value) => {
  for (const item of nodes) {
    if (item.value === value) {
      return item
    }

    if (item.children?.length) {
      const found = findNestedItemByValue(value, item.children)
      if (found) {
        return found
      }
    }
  }

  return null
}

const isRouteMatched = (targetPath) => {
  if (!targetPath) {
    return false
  }

  return route.path === targetPath || route.path.startsWith(`${targetPath}/`)
}

const syncActiveTab = () => {
  if (props.routeMode) {
    const routeMatchedItem = normalizedItems.value.find((item) => isRouteMatched(item.to))
    const fallback = props.defaultTab || normalizedItems.value[0]?.value || ''
    activeTab.value = routeMatchedItem?.value || fallback
    return
  }

  if (props.modelValue) {
    activeTab.value = props.modelValue
    return
  }

  const fallback = props.defaultTab || normalizedItems.value[0]?.value || ''
  const hasActive = normalizedItems.value.some((item) => item.value === activeTab.value)

  if (!hasActive) {
    activeTab.value = fallback
  }
}

watch(() => [props.items, props.defaultTab], syncActiveTab, { immediate: true, deep: true })
watch(() => route.path, syncActiveTab)
watch(() => props.modelValue, syncActiveTab)

const handleChange = (value) => {
  activeTab.value = value
  emit('update:modelValue', value)

  if (!props.routeMode) {
    return
  }

  const selectedItem = props.submenu ? findNestedItemByValue(value) : findItemByValue(value)
  if (!selectedItem?.to || selectedItem.to === route.path) {
    return
  }

  router.push(selectedItem.to)
}
</script>

<template>
  <SubNav
    v-if="submenu"
    :items="normalizedItems"
    :model-value="activeTab"
    :max-depth="submenuMaxDepth"
    @update:modelValue="handleChange"
  />

  <div
    v-else
    class="tabs-layout tabs-layout-vertical"
    :class="{
      'tabs-layout-vertical-divider': divider,
      'tabs-layout-fill': fill
    }"
  >
    <Tabs
      :model-value="activeTab"
      @update:modelValue="handleChange"
      :items="normalizedItems"
      orientation="vertical"
      :line="line"
      :line-frame="!divider"
    />

    <div
      v-if="showPanels"
      class="tabs-panel-container"
      :class="{ 'tabs-content-divider-vertical': divider }"
    >
      <transition name="tab-panel-fade" mode="out-in">
        <TabPanel
          v-if="activePanelItem"
          :key="activePanelItem.value"
          :active-value="activeTab"
          :panel-value="activePanelItem.value"
        >
          <component :is="activePanelItem.component" />
        </TabPanel>
      </transition>
    </div>
  </div>
</template>
