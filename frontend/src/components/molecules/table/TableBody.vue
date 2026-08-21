<script setup>
import TableCell from '@/components/atoms/table/TableCell.vue'
import TableRow from '@/components/atoms/table/TableRow.vue'

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
  clickableRows: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['row-click'])

const handleRowClick = (row) => {
  if (!props.clickableRows) {
    return
  }

  emit('row-click', row)
}
</script>

<template>
  <tbody>
    <TableRow v-if="loading">
      <TableCell class="table-empty" :colspan="columns.length">
        로딩 중...
      </TableCell>
    </TableRow>

    <TableRow v-else-if="rows.length === 0">
      <TableCell class="table-empty" :colspan="columns.length">
        {{ emptyText }}
      </TableCell>
    </TableRow>

    <TableRow
      v-for="row in rows"
      v-else
      :key="row[rowKey]"
      hover
      :class="{ 'cursor-pointer': clickableRows }"
      @click="handleRowClick(row)"
    >
      <TableCell
        v-for="column in columns"
        :key="column.key"
        :align="column.align ?? 'left'"
      >
        <slot :name="`cell-${column.key}`" :row="row" :column="column" :value="row[column.key]">
          {{ row[column.key] }}
        </slot>
      </TableCell>
    </TableRow>
  </tbody>
</template>
