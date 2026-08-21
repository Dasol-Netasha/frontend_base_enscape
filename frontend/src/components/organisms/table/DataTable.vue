<script setup>
import { computed, ref } from 'vue'

import TableBody from '@/components/molecules/table/TableBody.vue'
import TableHead from '@/components/molecules/table/TableHead.vue'

const props = defineProps({
  columns: {
    type: Array,
    default: () => []
  },
  rows: {
    type: Array,
    default: () => []
  },
  rowKey: {
    type: String,
    default: 'id'
  },
  loading: {
    type: Boolean,
    default: false
  },
  emptyText: {
    type: String,
    default: '데이터가 없습니다.'
  },
  sortable: {
    type: Boolean,
    default: false
  },
  initialSort: {
    type: Object,
    default: null
  },
  serverSort: {
    type: Boolean,
    default: false
  },
  clickableRows: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['sort-change', 'row-click'])

const activeSortKey = ref(props.initialSort?.key ?? '')
const activeSortDirection = ref(props.initialSort?.direction === 'desc' ? 'desc' : 'asc')

const normalizedColumns = computed(() => {
  return props.columns.map((column) => ({
    ...column,
    sortable: column.sortable ?? props.sortable
  }))
})

const inferSortType = (value) => {
  if (typeof value === 'number') {
    return 'number'
  }
  if (typeof value === 'string' && !Number.isNaN(Date.parse(value))) {
    return 'datetime'
  }
  return 'string'
}

const toComparable = (value, sortType) => {
  if (value === null || value === undefined) {
    return null
  }

  if (sortType === 'number') {
    const parsed = Number(value)
    return Number.isNaN(parsed) ? null : parsed
  }

  if (sortType === 'datetime') {
    const parsed = new Date(value).getTime()
    return Number.isNaN(parsed) ? null : parsed
  }

  return String(value).toLowerCase()
}

const sortedRows = computed(() => {
  if (props.serverSort) {
    return props.rows
  }

  const sortColumn = normalizedColumns.value.find((column) => column.key === activeSortKey.value)
  if (!sortColumn || !sortColumn.sortable) {
    return props.rows
  }

  const directionFactor = activeSortDirection.value === 'desc' ? -1 : 1
  const sampleValue = props.rows.find((row) => row?.[sortColumn.key] !== undefined)?.[sortColumn.key]
  const sortType = sortColumn.sortType ?? inferSortType(sampleValue)

  return props.rows
    .map((row, index) => ({ row, index }))
    .sort((a, b) => {
      const left = toComparable(a.row?.[sortColumn.key], sortType)
      const right = toComparable(b.row?.[sortColumn.key], sortType)

      if (left === right) {
        return a.index - b.index
      }
      if (left === null) {
        return 1
      }
      if (right === null) {
        return -1
      }

      if (left > right) {
        return 1 * directionFactor
      }
      if (left < right) {
        return -1 * directionFactor
      }
      return a.index - b.index
    })
    .map((item) => item.row)
})

const onSortColumn = (column) => {
  if (!column.sortable) {
    return
  }

  if (activeSortKey.value === column.key) {
    activeSortDirection.value = activeSortDirection.value === 'asc' ? 'desc' : 'asc'
    emit('sort-change', {
      key: activeSortKey.value,
      direction: activeSortDirection.value
    })
    return
  }

  activeSortKey.value = column.key
  activeSortDirection.value = column.initialSortDirection === 'desc' ? 'desc' : 'asc'
  emit('sort-change', {
    key: activeSortKey.value,
    direction: activeSortDirection.value
  })
}

const onRowClick = (row) => {
  emit('row-click', row)
}
</script>

<template>
  <div class="table-wrap">
    <table class="table-base">
      <TableHead
        :columns="normalizedColumns"
        :sort-key="activeSortKey"
        :sort-direction="activeSortDirection"
        @sort="onSortColumn"
      >
        <template v-for="column in normalizedColumns" :key="`header-${column.key}`" #[`header-${column.key}`]="slotProps">
          <slot :name="`header-${column.key}`" v-bind="slotProps" />
        </template>
      </TableHead>

      <TableBody
        :columns="normalizedColumns"
        :rows="sortedRows"
        :row-key="rowKey"
        :loading="loading"
        :empty-text="emptyText"
        :clickable-rows="clickableRows"
        @row-click="onRowClick"
      >
        <template v-for="column in normalizedColumns" :key="`cell-${column.key}`" #[`cell-${column.key}`]="slotProps">
          <slot :name="`cell-${column.key}`" v-bind="slotProps" />
        </template>
      </TableBody>
    </table>
  </div>
</template>
