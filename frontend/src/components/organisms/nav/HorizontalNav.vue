<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TabPanel from '@/components/molecules/TabPanel.vue'
import Tabs from '@/components/molecules/Tabs.vue'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
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
  align: {
    type: String,
    default: 'left',
    validator: (value) => ['left', 'center', 'right'].includes(value)
  },
  showPanels: {
    type: Boolean,
    default: false
  },
  routeMode: {
    type: Boolean,
    default: true
  }
})

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

  const fallback = props.defaultTab || normalizedItems.value[0]?.value || ''
  const hasActive = normalizedItems.value.some((item) => item.value === activeTab.value)

  if (!hasActive) {
    activeTab.value = fallback
  }
}

watch(() => [props.items, props.defaultTab], syncActiveTab, { immediate: true, deep: true })
watch(() => route.path, syncActiveTab)

const handleChange = (value) => {
  activeTab.value = value

  if (!props.routeMode) {
    return
  }

  const selectedItem = findItemByValue(value)
  if (!selectedItem?.to || selectedItem.to === route.path) {
    return
  }

  router.push(selectedItem.to)
}
</script>

<template>
  <div class="tabs-layout tabs-layout-horizontal">
    <Tabs
      :model-value="activeTab"
      @update:modelValue="handleChange"
      :items="normalizedItems"
      orientation="horizontal"
      :line="line"
      :line-frame="divider"
      :align="align"
    />

    <div v-if="showPanels" :class="{ 'tabs-content-divider-horizontal': divider }">
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
