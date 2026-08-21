<script setup>
import PageMetaInfo from '@/components/molecules/pagination/PageMetaInfo.vue'
import PageNavControls from '@/components/molecules/pagination/PageNavControls.vue'
import PageSizeSelector from '@/components/molecules/pagination/PageSizeSelector.vue'

const props = defineProps({
  page: {
    type: Number,
    required: true
  },
  pageSize: {
    type: Number,
    required: true
  },
  total: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  },
  pageSizeOptions: {
    type: Array,
    default: () => [10, 20, 30, 40, 50]
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:page', 'update:pageSize'])

const goToPage = (page) => {
  if (props.loading || page < 1 || page > props.totalPages || page === props.page) {
    return
  }
  emit('update:page', page)
}

const updatePageSize = (size) => {
  if (props.loading) {
    return
  }
  emit('update:pageSize', size)
}
</script>

<template>
  <div class="flex flex-wrap items-center justify-between gap-3">
    <div class="flex items-center">
      <PageSizeSelector
        :model-value="pageSize"
        :options="pageSizeOptions"
        :disabled="loading"
        @update:modelValue="updatePageSize"
      />
    </div>

    <div class="flex items-center justify-center">
      <PageNavControls
        :page="page"
        :total-pages="totalPages"
        :disabled="loading"
        @go-first="goToPage(1)"
        @go-prev="goToPage(page - 1)"
        @go-page="goToPage($event)"
        @go-next="goToPage(page + 1)"
        @go-last="goToPage(totalPages)"
      />
    </div>

    <div class="flex items-center justify-end">
      <PageMetaInfo :page="page" :page-size="pageSize" :total="total" />
    </div>
  </div>
</template>
