<script setup>
import { ref, watch } from 'vue'
import BaseChart from '@/components/organisms/chart/BaseChart.vue'
import { useThemeStore } from '@/stores/themeStore'
import { getChartThemeTokens } from '@/utils/chartTheme'
import { formatNumber } from '@/utils/formatData'

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
  smooth: {
    type: Boolean,
    default: true,
  },
  showArea: {
    type: Boolean,
    default: true,
  },
  showPoint: {
    type: Boolean,
    default: true,
  },
  height: {
    type: String,
    default: '320px',
  },
})

const baseChart = ref(null)
const themeStore = useThemeStore()

const extractNumericValue = (rawValue) => {
  if (Array.isArray(rawValue)) {
    return Number(rawValue[rawValue.length - 1])
  }

  if (typeof rawValue === 'object' && rawValue !== null) {
    return Number(rawValue.value)
  }

  return Number(rawValue)
}

const buildOption = () => {
  const theme = getChartThemeTokens()

  return {
    animationDuration: 600,
    color: ['#0ea5e9', '#f97316', '#10b981'],
    tooltip: {
      trigger: 'axis',
      appendToBody: true,
      backgroundColor: theme.surface2,
      borderColor: theme.borderSoft,
      borderWidth: 1,
      textStyle: {
        color: theme.textBody,
      },
      formatter: (params) => {
        const list = Array.isArray(params) ? params : [params]
        if (!list.length) {
          return ''
        }

        const title = String(list[0]?.axisValueLabel || list[0]?.name || '')
        const rows = list.map((item) => {
          const marker = String(item?.marker || '')
          const numericValue = extractNumericValue(item?.value)
          const formattedValue = formatNumber(numericValue, 0, '0')
          return `${marker}${item?.seriesName || ''}: <strong>${formattedValue}</strong>`
        })

        return `${title}<br/>${rows.join('<br/>')}`
      },
    },
    grid: { left: 16, right: 16, top: 64, bottom: 5, containLabel: true },
    legend: {
      top: 0,
      left: 14,
      textStyle: {
        color: theme.textBody,
      },
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: props.categories,
      axisLine: { lineStyle: { color: theme.borderSoft } },
      axisLabel: { color: theme.textSubtle },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: theme.borderSoft } },
      axisLabel: { color: theme.textSubtle },
    },
    series: props.series.map((item) => ({
      ...item,
      type: 'line',
      smooth: props.smooth,
      symbol: props.showPoint ? 'circle' : 'none',
      symbolSize: props.showPoint ? 7 : 0,
      areaStyle: props.showArea ? { opacity: 0.08 } : undefined,
      lineStyle: {
        ...(item.lineStyle || {}),
        width: 3,
      },
      itemStyle: {
        ...(item.itemStyle || {}),
      },
    })),
  }
}

watch(
  () => [props.categories, props.series, props.smooth, props.showArea, props.showPoint, themeStore.theme],
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
      <h3 class="card-title text-lg font-semibold">{{ title }}</h3>
    </header>
    <div :style="{ height }">
      <BaseChart ref="baseChart" @vue:mounted="onMounted" />
    </div>
  </section>
</template>
