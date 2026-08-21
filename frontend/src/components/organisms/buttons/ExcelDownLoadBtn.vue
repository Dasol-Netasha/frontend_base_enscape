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

const escapeHtml = (value) => {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

const toExcelHtml = () => {
  const headerCells = props.columns
    .map((column) => `<th style="border:1px solid #cbd5e1;padding:6px;background:#f8fafc;">${escapeHtml(column.label)}</th>`)
    .join('')

  const rowHtml = props.rows
    .map((row) => {
      const cells = props.columns
        .map((column) => `<td style="border:1px solid #e2e8f0;padding:6px;">${escapeHtml(row?.[column.key])}</td>`)
        .join('')
      return `<tr>${cells}</tr>`
    })
    .join('')

  return [
    '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">',
    '<head><meta charset="UTF-8"></head>',
    '<body><table>',
    `<thead><tr>${headerCells}</tr></thead>`,
    `<tbody>${rowHtml}</tbody>`,
    '</table></body>',
    '</html>',
  ].join('')
}

const onDownload = () => {
  if (props.disabled) {
    return
  }

  const fileName = `${sanitizeFileName(props.fileNamePrefix)}.xls`
  const blob = new Blob([toExcelHtml()], { type: 'application/vnd.ms-excel;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = fileName
  anchor.click()
  URL.revokeObjectURL(url)

  emit('downloaded', {
    format: 'excel',
    fileName,
    rowCount: props.rows.length,
    columnCount: props.columns.length,
  })
}
</script>

<template>
  <button
    type="button"
    class="mt-1 w-full rounded-lg px-3 py-2 text-left text-sm text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
    :disabled="disabled"
    @click="onDownload"
  >
    Excel 파일로 다운로드
  </button>
</template>
