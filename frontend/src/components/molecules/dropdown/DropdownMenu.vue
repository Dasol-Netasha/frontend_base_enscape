<script setup>
import DropdownItem from '@/components/atoms/DropdownItem.vue'

const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  activeKey: {
    type: [String, Number],
    default: ''
  }
})

const emit = defineEmits(['select'])

const handleSelect = (item) => {
  if (!item.disabled) {
    emit('select', item)
  }
}
</script>

<template>
  <div class="dropdown-menu" role="menu" aria-orientation="vertical">
    <template v-for="item in items" :key="item.key">
      <div v-if="item.type === 'divider'" class="dropdown-divider" role="separator" />
      <DropdownItem
        v-else
        :label="item.label"
        :danger="Boolean(item.danger)"
        :disabled="Boolean(item.disabled)"
        :active="item.key === activeKey"
        @select="handleSelect(item)"
      >
        <template v-if="item.icon" #icon>
          <component :is="item.icon" />
        </template>
      </DropdownItem>
    </template>
  </div>
</template>
