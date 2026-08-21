<script setup>
import Input from '@/components/atoms/Input.vue'

const modelValue = defineModel({ type: String, default: '' })
</script>

<template>
  <Input v-model="modelValue" type="password" placeholder="비밀번호" autocomplete="current-password" />
</template>
