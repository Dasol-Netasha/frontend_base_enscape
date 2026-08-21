<script setup>
import { computed } from 'vue'
import SortIconBtn from '@/components/molecules/buttons/SortIconBtn.vue'

const props = defineProps({
  align: {
    type: String,
    default: 'left'
  },
  sortable: {
    type: Boolean,
    default: false
  },
  sortDirection: {
    type: String,
    default: 'none'
  }
})

const emit = defineEmits(['sort'])

const alignClass = computed(() => {
  if (props.align === 'center') return 'table-cell-center'
  if (props.align === 'right') return 'table-cell-right'
  return 'table-cell-left'
})
</script>

<template>
  <th class="table-th" :class="[alignClass, { 'table-th-sortable': sortable }]">
    <div v-if="sortable" class="table-th-content">
      <span class="table-th-label">
        <slot />
      </span>
      <SortIconBtn
        :direction="sortDirection"
        aria-label="컬럼 정렬"
        @click="emit('sort')"
      />
    </div>
    <slot v-else />
  </th>
</template>
