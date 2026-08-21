<script setup>
import { computed, ref, watch } from 'vue'
import SubNavNode from '@/components/organisms/nav/SubNavNode.vue'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  modelValue: {
    type: String,
    default: ''
  },
  maxDepth: {
    type: Number,
    default: Number.MAX_SAFE_INTEGER
  }
})

const emit = defineEmits(['update:modelValue'])

const expandedKeys = ref([])

const findPathByKey = (nodes, key, path = []) => {
  for (const node of nodes) {
    const nextPath = [...path, node]

    if (node.key === key) {
      return nextPath
    }

    if (node.children?.length) {
      const found = findPathByKey(node.children, key, nextPath)
      if (found) {
        return found
      }
    }
  }

  return null
}

const selectableKeys = computed(() => {
  const keys = []

  const walk = (nodes) => {
    for (const node of nodes) {
      keys.push(node.key)
      if (node.children?.length) {
        walk(node.children)
      }
    }
  }

  walk(props.items)
  return keys
})

watch(
  () => props.modelValue,
  (activeKey) => {
    if (!activeKey) {
      return
    }

    const path = findPathByKey(props.items, activeKey)
    if (!path) {
      return
    }

    expandedKeys.value = path.slice(0, -1).map((item) => item.key)
  },
  { immediate: true }
)

watch(
  () => props.items,
  () => {
    if (!props.modelValue && selectableKeys.value.length > 0) {
      emit('update:modelValue', selectableKeys.value[0])
    }
  },
  { immediate: true, deep: true }
)

const handleToggle = (key) => {
  if (expandedKeys.value.includes(key)) {
    expandedKeys.value = expandedKeys.value.filter((itemKey) => itemKey !== key)
    return
  }

  expandedKeys.value = [...expandedKeys.value, key]
}

const handleSelect = (item) => {
  emit('update:modelValue', item.key)
}
</script>

<template>
  <nav class="subnav" aria-label="Sub navigation">
    <ul class="subnav-list">
      <SubNavNode
        v-for="item in items"
        :key="item.key"
        :item="item"
        :active-key="modelValue"
        :expanded-keys="expandedKeys"
        :max-depth="maxDepth"
        @toggle="handleToggle"
        @select="handleSelect"
      />
    </ul>
  </nav>
</template>
