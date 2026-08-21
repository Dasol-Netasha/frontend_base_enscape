<script setup>
import { computed } from 'vue'
import DownloadIconBtn from '@/components/molecules/buttons/DownloadIconBtn.vue'
import Dropdown from '@/components/organisms/dropdown/Dropdown.vue'
import CSVDownloadBtn from '@/components/organisms/buttons/CSVDownloadBtn.vue'
import ExcelDownLoadBtn from '@/components/organisms/buttons/ExcelDownLoadBtn.vue'

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
  triggerVariant: {
    type: String,
    default: undefined,
  },
  triggerSize: {
    type: String,
    default: undefined,
  },
  triggerRounded: {
    type: Boolean,
    default: undefined,
  },
  triggerOutlined: {
    type: Boolean,
    default: undefined,
  },
  triggerFlat: {
    type: Boolean,
    default: undefined,
  },
  triggerAriaLabel: {
    type: String,
    default: '데이터 다운로드',
  },
})

const emit = defineEmits(['download'])

const isDisabled = computed(() => props.disabled || props.columns.length === 0 || props.rows.length === 0)

const downloadButtonList = [
  {
    key: 'csv',
    component: CSVDownloadBtn,
  },
  {
    key: 'excel',
    component: ExcelDownLoadBtn,
  },
]

const onDownloaded = (payload, close) => {
  emit('download', payload)
  close()
}

const triggerProps = computed(() => ({
  variant: props.triggerVariant,
  size: props.triggerSize,
  rounded: props.triggerRounded,
  outlined: props.triggerOutlined,
  flat: props.triggerFlat,
  ariaLabel: props.triggerAriaLabel,
}))
</script>

<template>
  <Dropdown align="end">
    <template #trigger="{ isOpen, toggle }">
        <DownloadIconBtn
          v-bind="triggerProps"
          :disabled="isDisabled"
          :class="{ 'opacity-90': isOpen }"
          @click="toggle"
        />
    </template>

    <template #default="{ close }">
      <div>
        <component
          :is="item.component"
          v-for="item in downloadButtonList"
          :key="item.key"
          :columns="columns"
          :rows="rows"
          :file-name-prefix="fileNamePrefix"
          :disabled="isDisabled"
          @downloaded="onDownloaded($event, close)"
        />
      </div>
    </template>
  </Dropdown>
</template>
