<script setup>
import IconButton from '@/components/atoms/IconButton.vue'
import PageNavIcon from '@/components/atoms/pagination/PageNavIcon.vue'
import PageNumberButtons from '@/components/molecules/pagination/PageNumberButtons.vue'

const props = defineProps({
  page: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['go-first', 'go-prev', 'go-next', 'go-last', 'go-page'])
</script>

<template>
  <div class="flex items-center gap-1">
    <IconButton
      size="sm"
      flat
      aria-label="첫 페이지"
      :disabled="disabled || page <= 1"
      @click="emit('go-first')"
    >
      <PageNavIcon type="first" />
    </IconButton>

    <IconButton
      size="sm"
      flat
      aria-label="이전 페이지"
      :disabled="disabled || page <= 1"
      @click="emit('go-prev')"
    >
      <PageNavIcon type="prev" />
    </IconButton>

    <PageNumberButtons
      :page="page"
      :total-pages="totalPages"
      :disabled="disabled"
      @go-page="emit('go-page', $event)"
    />

    <IconButton
      size="sm"
      flat
      aria-label="다음 페이지"
      :disabled="disabled || page >= totalPages"
      @click="emit('go-next')"
    >
      <PageNavIcon type="next" />
    </IconButton>

    <IconButton
      size="sm"
      flat
      aria-label="마지막 페이지"
      :disabled="disabled || page >= totalPages"
      @click="emit('go-last')"
    >
      <PageNavIcon type="last" />
    </IconButton>
  </div>
</template>
