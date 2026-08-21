import { computed, onMounted, onUnmounted, ref } from 'vue'
import { formatData } from '@/utils/formatData'

// 현재 시간을 1초 단위로 갱신해 헤더/상태바 같은 실시간 UI에 공급한다.
export const useCurrentTime = () => {
  const now = ref(new Date())
  let timerId = null

  // 화면 표시용 포맷과 machine-readable datetime 값을 함께 제공한다.
  const currentTimeText = computed(() => {
    return formatData(now.value, { type: 'datetime' })
  })

  const currentDateTimeAttr = computed(() => now.value.toISOString())

  onMounted(() => {
    timerId = window.setInterval(() => {
      now.value = new Date()
    }, 1000)
  })

  onUnmounted(() => {
    if (timerId) {
      window.clearInterval(timerId)
    }
  })

  return {
    currentTimeText,
    currentDateTimeAttr
  }
}
