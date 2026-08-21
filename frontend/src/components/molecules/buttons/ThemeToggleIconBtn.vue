<script setup>
import { computed } from 'vue'
import IconButton from '@/components/atoms/IconButton.vue'
import MoonIcon from '@/components/atoms/icons/MoonIcon.vue'
import SunIcon from '@/components/atoms/icons/SunIcon.vue'

const props = defineProps({
  isDark: {
    type: Boolean,
    default: false,
  },
  variant: {
    type: String,
    default: 'ghost',
  },
  size: {
    type: String,
    default: 'md',
  },
  rounded: {
    type: Boolean,
    default: true,
  },
  outlined: {
    type: Boolean,
    default: true,
  },
  flat: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['click'])

const ariaLabel = computed(() => (props.isDark ? '밝은 모드로 변경' : '어두운 모드로 변경'))
</script>

<template>
  <IconButton
    :variant="variant"
    :size="size"
    :rounded="rounded"
    :outlined="outlined"
    :flat="flat"
    :disabled="disabled"
    :aria-label="ariaLabel"
    @click="emit('click', $event)"
  >
    <SunIcon v-if="isDark" />
    <MoonIcon v-else />
  </IconButton>
</template>
