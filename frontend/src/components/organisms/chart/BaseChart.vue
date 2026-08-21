<script setup>
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref } from 'vue'

const chartEl = ref(null)
let chart

const getInstance = () => chart

const setOption = (option) => {
  if (!chart) return
  chart.setOption(option)
}

const handleResize = () => {
  chart?.resize()
}

onMounted(() => {
  chart = echarts.init(chartEl.value)
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})

defineExpose({ setOption, getInstance })
</script>

<template>
  <div ref="chartEl" class="h-full w-full" />
</template>
