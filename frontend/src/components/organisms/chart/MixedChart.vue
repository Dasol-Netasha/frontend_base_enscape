<script setup>
import { ref, watch } from 'vue'
import BaseChart from '@/components/organisms/chart/BaseChart.vue'

/**
 * MixedChart — 바 + 라인 혼합 차트
 *
 * series 아이템에 `chartType: 'bar' | 'line'` 을 지정하면 됩니다.
 * 생략 시 기본값은 'bar'.
 *
 * yAxisIndex를 2축(0/1)으로 지정하면 좌/우 이중 Y축을 쓸 수 있습니다.
 * 이중 Y축을 쓸 때는 `dualYAxis: true` prop을 넘겨주세요.
 *
 * 예)
 * :series="[
 *   { name: '불량 수',  data: [...], chartType: 'bar' },
 *   { name: '불량률(%)', data: [...], chartType: 'line', yAxisIndex: 1 },
 * ]"
 * :dualYAxis="true"
 */

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
  /** 우측 보조 Y축 활성화 */
  dualYAxis: {
    type: Boolean,
    default: false,
  },
  height: {
    type: String,
    default: '320px',
  },
})

const baseChart = ref(null)

const baseYAxis = {
  type: 'value',
  axisLine: { show: false },
  splitLine: { lineStyle: { color: '#e2e8f0' } },
  axisLabel: { color: '#64748b' },
}

const buildOption = () => ({
  animationDuration: 600,
  color: ['#0ea5e9', '#f97316', '#10b981', '#a855f7', '#f43f5e'],
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true },
  grid: { left: 16, right: props.dualYAxis ? 48 : 16, top: 56, bottom: 16, containLabel: true },
  legend: { top: 14, left: 14 },
  xAxis: {
    type: 'category',
    data: props.categories,
    axisLine: { lineStyle: { color: '#cbd5e1' } },
    axisLabel: { color: '#64748b' },
    axisTick: { show: false },
  },
  yAxis: props.dualYAxis
    ? [
        { ...baseYAxis },
        { ...baseYAxis, splitLine: { show: false } },
      ]
    : [{ ...baseYAxis }],
  series: props.series.map(({ chartType = 'bar', ...item }) => {
    if (chartType === 'line') {
      return {
        ...item,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 7,
        lineStyle: { width: 3 },
        z: 10,
      }
    }
    return {
      ...item,
      type: 'bar',
      barMaxWidth: 48,
      itemStyle: { borderRadius: [6, 6, 0, 0] },
    }
  }),
})

watch(
  () => [props.categories, props.series, props.dualYAxis],
  () => baseChart.value?.setOption(buildOption()),
  { deep: true },
)

const onMounted = () => {
  baseChart.value?.setOption(buildOption())
}
</script>

<template>
  <section class="overflow-hidden card">
    <header class="mb-4">
      <h3 class="text-lg font-semibold text-slate-950">{{ title }}</h3>
    </header>
    <div :style="{ height }">
      <BaseChart ref="baseChart" @vue:mounted="onMounted" />
    </div>
  </section>
</template>
