<script setup>
const props = defineProps({
  columns: {
    type: Array,
    default: () => [],
  },
  rows: {
    type: Array,
    default: () => [],
  },
  fileNamePrefix: {
    type: String,
    default: 'data-table',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['downloaded'])

const sanitizeFileName = (value) => {
  const normalized = String(value ?? '').trim().replace(/[\\/:*?"<>|]+/g, '_')
  return normalized || 'data-table'
}

const escapeCsvField = (value) => {
  if (value === null || value === undefined) {
    return ''
  }
  const text = String(value)
  if (/[",\n\r]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`
  }
  return text
}

const toCsv = () => {
  const headers = props.columns.map((column) => escapeCsvField(column.label))
  const body = props.rows.map((row) =>
    props.columns.map((column) => escapeCsvField(row?.[column.key] ?? '')).join(','),
  )
  return [headers.join(','), ...body].join('\r\n')
}

const onDownload = () => {
  if (props.disabled) {
    return
  }

  const fileName = `${sanitizeFileName(props.fileNamePrefix)}.csv`
  const blob = new Blob([`\uFEFF${toCsv()}`], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = fileName
  anchor.click()
  URL.revokeObjectURL(url)

  emit('downloaded', {
    format: 'csv',
    fileName,
    rowCount: props.rows.length,
    columnCount: props.columns.length,
  })
}
</script>

<template>
  <button
    type="button"
    class="w-full rounded-lg px-3 py-2 text-left text-sm text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
    :disabled="disabled"
    @click="onDownload"
  >
    CSV 파일로 다운로드
  </button>
</template>
