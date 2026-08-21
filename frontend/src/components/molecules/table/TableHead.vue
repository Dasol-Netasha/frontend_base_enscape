<script setup>
import BilingualLabel from '@/components/molecules/labels/BilingualLabel.vue'
import TableHeaderCell from '@/components/atoms/table/TableHeaderCell.vue'
import TableRow from '@/components/atoms/table/TableRow.vue'

const props = defineProps({
  columns: {
    type: Array,
    default: () => []
  },
  sortKey: {
    type: String,
    default: ''
  },
  sortDirection: {
    type: String,
    default: 'asc'
  }
})

const emit = defineEmits(['sort'])

const getSortDirection = (column) => {
  if (!column.sortable) {
    return 'none'
  }
  return props.sortKey === column.key ? props.sortDirection : 'none'
}
</script>

<template>
  <thead>
    <TableRow>
      <TableHeaderCell
        v-for="column in columns"
        :key="column.key"
        :align="column.align ?? 'left'"
        :sortable="column.sortable ?? false"
        :sort-direction="getSortDirection(column)"
        @sort="emit('sort', column)"
      >
        <slot :name="`header-${column.key}`" :column="column">
          <BilingualLabel :label="column.label" :show-tooltip="false" />
        </slot>
      </TableHeaderCell>
    </TableRow>
  </thead>
</template>
