<script setup>
import PageIndexText from '@/components/atoms/pagination/PageIndexText.vue'
import TotalCountText from '@/components/atoms/pagination/TotalCountText.vue'

defineProps({
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
  }
})
</script>

<template>
  <div class="flex items-center gap-2">
    <PageIndexText :page="page" :page-size="pageSize" :total="total" />
    /
    <TotalCountText :total="total" />
  </div>
</template>
