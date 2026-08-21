<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import BilingualLabel from '@/components/molecules/labels/BilingualLabel.vue'

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
  modelValue: {
    type: Object,
    default: () => ({ from: '', to: '' }),
  },
  required: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const rootRef = ref(null)
const isOpen = ref(false)
const activeSide = ref('from')
const viewingMonth = ref(startOfMonth(new Date()))

function parseYmd(value) {
  if (!value || typeof value !== 'string') {
    return null
  }
  const [y, m, d] = value.split('-').map((part) => Number(part))
  if (!y || !m || !d) {
    return null
  }
  const parsed = new Date(y, m - 1, d)
  if (
    parsed.getFullYear() !== y ||
    parsed.getMonth() !== m - 1 ||
    parsed.getDate() !== d
  ) {
    return null
  }
  parsed.setHours(0, 0, 0, 0)
  return parsed
}

function toYmd(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function startOfMonth(date) {
  return new Date(date.getFullYear(), date.getMonth(), 1)
}

function sameDay(a, b) {
  if (!a || !b) {
    return false
  }
  return toYmd(a) === toYmd(b)
}

const fromDate = computed(() => parseYmd(props.modelValue?.from))
const toDate = computed(() => parseYmd(props.modelValue?.to))

const displayFrom = computed(() => props.modelValue?.from || '부터')
const displayTo = computed(() => props.modelValue?.to || '까지')
const monthTitle = computed(() => {
  const y = viewingMonth.value.getFullYear()
  const m = String(viewingMonth.value.getMonth() + 1).padStart(2, '0')
  return `${y}.${m}`
})

const calendarCells = computed(() => {
  const first = startOfMonth(viewingMonth.value)
  const firstWeekday = first.getDay()
  const daysInMonth = new Date(first.getFullYear(), first.getMonth() + 1, 0).getDate()
  const cells = []

  for (let i = 0; i < firstWeekday; i += 1) {
    cells.push({ key: `empty-${i}`, empty: true })
  }

  for (let day = 1; day <= daysInMonth; day += 1) {
    const date = new Date(first.getFullYear(), first.getMonth(), day)
    date.setHours(0, 0, 0, 0)
    cells.push({ key: toYmd(date), empty: false, date, day })
  }

  return cells
})

const hasRange = computed(() => Boolean(fromDate.value && toDate.value))

const inSelectedRange = (target) => {
  if (!fromDate.value || !toDate.value || !target) {
    return false
  }
  return target >= fromDate.value && target <= toDate.value
}

const isBoundary = (target) => sameDay(target, fromDate.value) || sameDay(target, toDate.value)

const openPicker = (side) => {
  activeSide.value = side
  const seed = side === 'to' ? toDate.value || fromDate.value : fromDate.value || toDate.value
  viewingMonth.value = startOfMonth(seed || new Date())
  isOpen.value = true
}

const moveMonth = (offset) => {
  viewingMonth.value = new Date(viewingMonth.value.getFullYear(), viewingMonth.value.getMonth() + offset, 1)
}

const clearRange = () => {
  emit('update:modelValue', { from: '', to: '' })
}

const selectDate = (selectedDate) => {
  const from = fromDate.value
  const to = toDate.value
  const next = { from: props.modelValue?.from || '', to: props.modelValue?.to || '' }

  if (activeSide.value === 'from') {
    next.from = toYmd(selectedDate)
    if (to && selectedDate > to) {
      next.to = ''
    }
    emit('update:modelValue', next)
    activeSide.value = 'to'
    return
  }

  if (!from) {
    next.from = toYmd(selectedDate)
    next.to = ''
    emit('update:modelValue', next)
    activeSide.value = 'to'
    return
  }

  if (selectedDate < from) {
    next.from = toYmd(selectedDate)
    next.to = toYmd(from)
  } else {
    next.to = toYmd(selectedDate)
  }

  emit('update:modelValue', next)
}

const onClickOutside = (event) => {
  if (!isOpen.value) {
    return
  }
  if (!rootRef.value?.contains(event.target)) {
    isOpen.value = false
  }
}

watch(
  () => props.modelValue,
  () => {
    if (!isOpen.value) {
      const seed = fromDate.value || toDate.value
      if (seed) {
        viewingMonth.value = startOfMonth(seed)
      }
    }
  },
  { deep: true },
)

onMounted(() => {
  document.addEventListener('mousedown', onClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onClickOutside)
})
</script>

<template>
  <div ref="rootRef" class="relative flex flex-col gap-1">
    <label class="text-xs font-medium text-slate-600">
      <BilingualLabel :label="label" />
      <span v-if="required" class="ml-0.5 text-rose-500">*</span>
    </label>

    <div class="flex items-center gap-1">
      <button type="button" class="input-base input-sm text-left" @click="openPicker('from')">
        {{ displayFrom }}
      </button>
      <span class="text-xs text-slate-400">~</span>
      <button type="button" class="input-base input-sm text-left" @click="openPicker('to')">
        {{ displayTo }}
      </button>
      <button type="button" class="rounded-md px-2 py-1 text-xs text-slate-500 hover:bg-slate-100" @click="clearRange">
        초기화
      </button>
    </div>

    <div
      v-if="isOpen"
      class="absolute left-0 top-[calc(100%+6px)] z-40 w-[280px] rounded-xl border border-slate-200 bg-white p-3 shadow-xl"
    >
      <div class="mb-2 flex items-center justify-between">
        <button type="button" class="rounded-md px-2 py-1 text-xs text-slate-500 hover:bg-slate-100" @click="moveMonth(-1)">
          이전
        </button>
        <p class="text-sm font-semibold text-slate-700">{{ monthTitle }}</p>
        <button type="button" class="rounded-md px-2 py-1 text-xs text-slate-500 hover:bg-slate-100" @click="moveMonth(1)">
          다음
        </button>
      </div>

      <div class="mb-2 grid grid-cols-7 text-center text-[11px] text-slate-400">
        <span>일</span><span>월</span><span>화</span><span>수</span><span>목</span><span>금</span><span>토</span>
      </div>

      <div class="grid grid-cols-7 gap-1">
        <template v-for="cell in calendarCells" :key="cell.key">
          <span v-if="cell.empty" class="h-8" />
          <button
            v-else
            type="button"
            class="h-8 rounded-md text-sm transition"
            :class="[
              isBoundary(cell.date)
                ? 'bg-slate-800 font-semibold text-white'
                : inSelectedRange(cell.date)
                  ? 'bg-slate-100 text-slate-800'
                  : 'text-slate-700 hover:bg-slate-100',
            ]"
            @click="selectDate(cell.date)"
          >
            {{ cell.day }}
          </button>
        </template>
      </div>

      <p class="mt-3 text-[11px] text-slate-500">
        {{ hasRange ? `${displayFrom} ~ ${displayTo}` : '기간 범위를 선택하세요.' }}
      </p>
    </div>
  </div>
</template>