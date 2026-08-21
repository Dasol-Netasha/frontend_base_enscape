<script setup>
import { computed } from 'vue'

defineOptions({
  name: 'SubNavNode'
})

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 1
  },
  activeKey: {
    type: String,
    default: ''
  },
  expandedKeys: {
    type: Array,
    default: () => []
  },
  maxDepth: {
    type: Number,
    default: Number.MAX_SAFE_INTEGER
  }
})

const emit = defineEmits(['toggle', 'select'])

const hasChildren = computed(() => Array.isArray(props.item.children) && props.item.children.length > 0)
const canShowChildren = computed(() => props.level < props.maxDepth)
const isExpanded = computed(() => props.expandedKeys.includes(props.item.key))

const hasActiveDescendant = (node, activeKey) => {
  if (!node?.children?.length) {
    return false
  }

  for (const child of node.children) {
    if (child.key === activeKey) {
      return true
    }

    if (hasActiveDescendant(child, activeKey)) {
      return true
    }
  }

  return false
}

const isActive = computed(() => {
  return props.activeKey === props.item.key || hasActiveDescendant(props.item, props.activeKey)
})

const rowStyle = computed(() => ({
  paddingLeft: `${0.75 + (props.level - 1) * 0.85}rem`
}))

const handleRowClick = () => {
  if (hasChildren.value && canShowChildren.value) {
    emit('toggle', props.item.key)
  }

  emit('select', props.item)
}
</script>

<template>
  <li class="subnav-node">
    <button
      type="button"
      class="subnav-row"
      :class="{
        'subnav-row-active': isActive,
        'subnav-row-parent': hasChildren
      }"
      :style="rowStyle"
      @click="handleRowClick"
    >
      <span class="subnav-label">{{ item.label }}</span>
      <span v-if="hasChildren && canShowChildren" class="subnav-chevron" :class="{ 'subnav-chevron-open': isExpanded }">▾</span>
    </button>

    <transition name="subnav-collapse">
      <ul v-if="hasChildren && canShowChildren && isExpanded" class="subnav-children">
        <SubNavNode
          v-for="child in item.children"
          :key="child.key"
          :item="child"
          :level="level + 1"
          :active-key="activeKey"
          :expanded-keys="expandedKeys"
          :max-depth="maxDepth"
          @toggle="emit('toggle', $event)"
          @select="emit('select', $event)"
        />
      </ul>
    </transition>
  </li>
</template>
