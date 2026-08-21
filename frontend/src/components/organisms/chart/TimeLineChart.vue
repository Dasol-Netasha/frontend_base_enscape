<script setup>
import { computed } from 'vue'

import LineChart from '@/components/organisms/chart/LineChart.vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  categories: {
    type: Array,
    required: true,
  },
  series: {
    type: Array,
    required: true,
  },
  maxVisiblePoints: {
    type: Number,
    default: 30,
  },
  height: {
    type: String,
    default: '320px',
  },
})

const startIndex = computed(() => {
  return Math.max(props.categories.length - props.maxVisiblePoints, 0)
})

const visibleCategories = computed(() => {
  return props.categories.slice(startIndex.value)
})

const visibleSeries = computed(() => {
  return props.series.map((item) => ({
    ...item,
    data: Array.isArray(item?.data) ? item.data.slice(startIndex.value) : [],
  }))
})
</script>

<template>
  <LineChart
    :title="title"
    :categories="visibleCategories"
    :series="visibleSeries"
    :height="height"
    :smooth="true"
    :show-area="true"
    :show-point="false"
  />
</template>
