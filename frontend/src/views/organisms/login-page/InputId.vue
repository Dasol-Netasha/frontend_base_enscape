<script setup>
import Input from '@/components/atoms/Input.vue'

const modelValue = defineModel({ type: String, default: '' })
</script>

<template>
  <Input v-model="modelValue" placeholder="아이디" autocomplete="username" />
</template>
