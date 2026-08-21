import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const toTimeLabel = (date = new Date()) => {
  return new Intl.DateTimeFormat('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).format(date)
}

export const useTimeSeriesBuffer = (options = {}) => {
  const maxPoints = Number(options.maxPoints ?? 30)
  const intervalMs = Number(options.intervalMs ?? 1000)
  const seriesNames = Array.isArray(options.seriesNames) && options.seriesNames.length
    ? options.seriesNames
    : ['Value']

  const labels = ref([])
  const valuesBySeries = ref(seriesNames.map(() => []))
  const isRunning = ref(false)

  let timerId = null

  const trimToMax = () => {
    if (labels.value.length <= maxPoints) {
      return
    }

    const overflow = labels.value.length - maxPoints
    labels.value.splice(0, overflow)
    valuesBySeries.value = valuesBySeries.value.map((seriesValues) => {
      const nextValues = [...seriesValues]
      nextValues.splice(0, overflow)
      return nextValues
    })
  }

  const pushPoint = (point) => {
    const timeLabel = String(point?.label ?? toTimeLabel())
    const values = Array.isArray(point?.values) ? point.values : [point?.value]

    labels.value.push(timeLabel)
    valuesBySeries.value = valuesBySeries.value.map((seriesValues, index) => {
      return [...seriesValues, Number(values[index] ?? 0)]
    })

    trimToMax()
  }

  const categories = computed(() => labels.value)
  const series = computed(() => {
    return seriesNames.map((name, index) => ({
      name,
      data: valuesBySeries.value[index] ?? [],
    }))
  })

  const stop = () => {
    if (timerId) {
      clearInterval(timerId)
      timerId = null
    }
    isRunning.value = false
  }

  const start = () => {
    if (timerId || typeof options.makePoint !== 'function') {
      return
    }

    isRunning.value = true
    timerId = setInterval(() => {
      const nextPoint = options.makePoint()
      pushPoint(nextPoint)
    }, intervalMs)
  }

  const reset = () => {
    labels.value = []
    valuesBySeries.value = seriesNames.map(() => [])
  }

  onMounted(() => {
    if (options.autoStart && typeof options.makePoint === 'function') {
      start()
    }
  })

  onBeforeUnmount(() => {
    stop()
  })

  return {
    categories,
    series,
    isRunning,
    pushPoint,
    start,
    stop,
    reset,
  }
}
