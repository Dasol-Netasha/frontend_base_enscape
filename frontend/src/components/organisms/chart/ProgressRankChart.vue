<script setup>
defineProps({
  title: {
    type: String,
    default: '랭킹',
  },
  items: {
    type: Array,
    default: () => [],
  },
  total: {
    type: Number,
    default: 0,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  emptyText: {
    type: String,
    default: '표시할 데이터가 없습니다.',
  },
})
</script>

<template>
  <div class="card">
    <div class="mb-3 flex items-center justify-between">
      <h3 class="card-title text-lg font-semibold">{{ title }}</h3>
    </div>

    <ul class="space-y-3">
      <li v-for="item in items" :key="item.feature_key || item.key || item.label" class="space-y-1">
        <div class="iq-progress-meta flex items-center justify-between text-xs">
          <span>{{ item.label_ko || item.label || item.feature_key || '-' }}</span>
          <span>{{ item.abnormal_count ?? item.value ?? 0 }}건 / {{ total }}건</span>
        </div>
        <div class="iq-progress-track h-3 rounded-full">
          <div
            class="h-3 rounded-full bg-gradient-to-r from-sky-500 to-cyan-400"
            :style="{ width: `${Math.min(item.share || 0, 100)}%` }"
          />
        </div>
      </li>
    </ul>

    <p v-if="!loading && !items.length" class="iq-empty-text text-xs">
      {{ emptyText }}
    </p>
  </div>
</template>
