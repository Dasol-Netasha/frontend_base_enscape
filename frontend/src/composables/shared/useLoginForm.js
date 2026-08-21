import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

export const useLoginForm = ({ redirectTo = '/main' } = {}) => {
  const router = useRouter()
  const authStore = useAuthStore()

  const id = ref('')
  const password = ref('')
  const errorMessage = ref('')

  const handleSubmit = () => {
    const success = authStore.login(id.value, password.value)
    if (success) {
      errorMessage.value = ''
      router.push(redirectTo)
      return
    }
    errorMessage.value = '아이디 또는 비밀번호가 올바르지 않습니다.'
  }

  return {
    id,
    password,
    errorMessage,
    handleSubmit,
  }
}
