<script setup>
import { useCurrentTime } from '@/composables/time/useCurrentTime'

const { currentTimeText, currentDateTimeAttr } = useCurrentTime()
</script>

<template>
  <time class="text-sm tabular-nums text-slate-600" :datetime="currentDateTimeAttr">
    {{ currentTimeText }}
  </time>
</template>
