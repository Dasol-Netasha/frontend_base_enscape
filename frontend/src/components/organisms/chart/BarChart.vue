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
  /**
   * 'grouped' | 'stacked'
   * grouped: 그룹 막대, stacked: 누적 막대
   */
  stack: {
    type: Boolean,
    default: false,
  },
  orientation: {
    type: String,
    default: 'vertical',
  },
  height: {
    type: String,
    default: '320px',
  },
  showLegend: {
    type: Boolean,
    default: true,
  },
  showAllValuesInTooltip: {
    type: Boolean,
    default: false,
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
  const isHorizontal = props.orientation === 'horizontal'
  const gridTop = props.showLegend ? 56 : 10
  const isNumber = (value) => typeof value === 'number' && Number.isFinite(value)
  const theme = getChartThemeTokens()

  const withDirectionalStyle = (data) => {
    if (!Array.isArray(data)) {
      return []
    }

    return data.map((value) => {
      const numericValue = isNumber(value) ? value : Number(value)
      const safeValue = Number.isFinite(numericValue) ? numericValue : 0

      if (!isHorizontal || props.stack) {
        return safeValue
      }

      return {
        value: safeValue,
        itemStyle: {
          borderRadius: safeValue < 0 ? [6, 0, 0, 6] : [0, 6, 6, 0],
          borderColor: '#e2e8f0',
          borderWidth: 1,
        },
      }
    })
  }

  return {
    animationDuration: 600,
    color: ['#0ea5e9', '#f97316', '#10b981', '#a855f7', '#f43f5e'],
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true,
      backgroundColor: theme.surface2,
      borderColor: theme.borderSoft,
      borderWidth: 1,
      textStyle: {
        color: theme.textBody,
      },
      formatter: (params) => {
        if (props.showAllValuesInTooltip) {
          const activeSeries = props.series?.[0]
          const data = Array.isArray(activeSeries?.data) ? activeSeries.data : []
          const rows = props.categories.map((category, index) => {
            const numericValue = extractNumericValue(data[index])
            return `${category}: <strong>${formatNumber(numericValue, 2, '0')}</strong>`
          })

          return rows.join('<br/>')
        }

        const list = Array.isArray(params) ? params : [params]
        if (!list.length) {
          return ''
        }

        const title = String(list[0]?.axisValueLabel || list[0]?.name || '')
        const rows = list.map((item) => {
          const marker = String(item?.marker || '')
          const numericValue = extractNumericValue(item?.value)
          const formattedValue = props.showAllValuesInTooltip
            ? formatNumber(numericValue, 2, '0')
            : formatNumber(numericValue, 0, '0')
          return `${marker}${item?.seriesName || ''}: <strong>${formattedValue}</strong>`
        })

        return `${title}<br/>${rows.join('<br/>')}`
      },
    },
    grid: { left: 16, right: 16, top: gridTop, bottom: 16, containLabel: true },
    legend: props.showLegend
      ? {
          top: 14,
          left: 14,
          textStyle: {
            color: theme.textBody,
          },
        }
      : { show: false },
    xAxis: {
      type: isHorizontal ? 'value' : 'category',
      data: isHorizontal ? undefined : props.categories,
      axisLine: { lineStyle: { color: theme.borderSoft } },
      axisLabel: { color: theme.textSubtle },
      axisTick: { show: false },
      splitLine: isHorizontal ? { lineStyle: { color: theme.borderSoft } } : { show: false },
    },
    yAxis: {
      type: isHorizontal ? 'category' : 'value',
      data: isHorizontal ? props.categories : undefined,
      axisLine: { show: isHorizontal },
      splitLine: isHorizontal ? { show: false } : { lineStyle: { color: theme.borderSoft } },
      axisLabel: { color: theme.textSubtle },
      axisTick: { show: false },
    },
    series: props.series.map((item) => ({
      ...item,
      type: 'bar',
      barMaxWidth: 48,
      stack: props.stack ? 'total' : undefined,
      data: withDirectionalStyle(item.data),
      itemStyle: {
        ...(item.itemStyle || {}),
        borderRadius: props.stack
          ? [0, 0, 0, 0]
          : isHorizontal
            ? [0, 6, 6, 0]
            : [6, 6, 0, 0],
      },
    })),
  }
}

watch(
  () => [props.categories, props.series, props.stack, props.orientation, props.showLegend, props.showAllValuesInTooltip, themeStore.theme],
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
