<script setup>
import InputId from '@/views/organisms/login-page/InputId.vue'
import InputPW from '@/views/organisms/login-page/InputPW.vue'
import LoginBtn from '@/views/organisms/login-page/LoginBtn.vue'
import { useLoginForm } from '@/composables/shared/useLoginForm'

const { id, password, errorMessage, handleSubmit } = useLoginForm()
</script>

<template>
  <div
    class="w-full max-w-sm rounded-2xl border p-8"
    style="border-color: var(--theme-border-soft); background: var(--theme-section-bg)"
  >
    <h1 class="text-xl font-semibold text-center">로그인</h1>
    <p class="mt-1 text-sm theme-text-muted text-center">계정 정보를 입력해 주세요.</p>

    <form class="mt-6 flex flex-col gap-3" @submit.prevent="handleSubmit">
      <InputId v-model="id" />
      <InputPW v-model="password" />

      <p v-if="errorMessage" class="text-sm" style="color: var(--theme-danger-bg)">
        {{ errorMessage }}
      </p>

      <LoginBtn class="mt-3" />
    </form>
  </div>
</template>
