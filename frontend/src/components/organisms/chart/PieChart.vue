<script setup>
import { ref, watch } from 'vue'
import { useThemeStore } from '@/stores/themeStore'

import BaseChart from '@/components/organisms/chart/BaseChart.vue'
import { getChartThemeTokens } from '@/utils/chartTheme'
import { formatNumber } from '@/utils/formatData'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  series: {
    type: Array,
    required: true,
  },
  donut: {
    type: Boolean,
    default: false,
  },
  innerRadius: {
    type: String,
    default: '48%',
  },
  outerRadius: {
    type: String,
    default: '76%',
  },
  height: {
    type: String,
    default: '320px',
  },
  legendLeft: {
    type: Boolean,
    default: false,
  },
  hideZeroValueLabels: {
    type: Boolean,
    default: false,
  },
})

const baseChart = ref(null)
const themeStore = useThemeStore()

const buildOption = () => {
  const theme = getChartThemeTokens()
  const chartData = props.series.map((item) => {
    const value = Number(item?.value || 0)
    if (!props.hideZeroValueLabels || value > 0) {
      return item
    }

    return {
      ...item,
      label: {
        ...(item?.label || {}),
        show: false,
      },
      labelLine: {
        ...(item?.labelLine || {}),
        show: false,
      },
    }
  })

  return {
    animationDuration: 600,
    color: ['#0ea5e9', '#f97316', '#10b981', '#a855f7', '#f43f5e', '#14b8a6'],
    tooltip: {
      trigger: 'item',
      appendToBody: true,
      formatter: (params) => {
        const name = String(params?.name || '')
        const value = Number(params?.value || 0)
        const percent = Number(params?.percent || 0)
        return `${name}: <strong>${formatNumber(value, 0, '0')}</strong> (${percent}%)`
      },
      backgroundColor: theme.surface2,
      borderColor: theme.borderSoft,
      borderWidth: 1,
      textStyle: {
        color: theme.textBody,
      },
    },
    legend: props.legendLeft
      ? {
          orient: 'vertical',
          left: 8,
          top: 'middle',
          textStyle: {
            color: theme.textBody,
          },
        }
      : {
          top: 14,
          left: 14,
          textStyle: {
            color: theme.textBody,
          },
        },
    series: [
      {
        name: props.title,
        type: 'pie',
        radius: props.donut ? [props.innerRadius, props.outerRadius] : ['0%', props.outerRadius],
        center: props.legendLeft ? ['62%', '56%'] : ['50%', '56%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderColor: theme.surface1,
          borderWidth: 2,
        },
        label: {
          color: theme.textBody,
        },
        labelLine: {
          lineStyle: {
            color: theme.borderSoft,
          },
        },
        emphasis: {
          label: {
            fontWeight: 700,
            color: theme.textStrong,
          },
        },
        data: chartData,
      },
    ],
  }
}

watch(
  () => [props.series, props.donut, props.innerRadius, props.outerRadius, props.legendLeft, props.hideZeroValueLabels, themeStore.theme],
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
