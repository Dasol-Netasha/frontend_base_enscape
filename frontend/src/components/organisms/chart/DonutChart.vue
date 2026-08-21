<script setup>
import PieChart from '@/components/organisms/chart/PieChart.vue'

defineProps({
  title: {
    type: String,
    required: true,
  },
  series: {
    type: Array,
    required: true,
  },
  innerRadius: {
    type: String,
    default: '52%',
  },
  outerRadius: {
    type: String,
    default: '76%',
  },
  height: {
    type: String,
    default: '320px',
  },
})
</script>

<template>
  <PieChart
    :title="title"
    :series="series"
    :donut="true"
    :inner-radius="innerRadius"
    :outer-radius="outerRadius"
    :height="height"
  />
</template>
