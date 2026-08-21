import { ref } from 'vue'

export const useAsyncState = (initialValue) => {
  const data = ref(initialValue)
  const loading = ref(false)
  const error = ref(null)

  const run = async (fetcher) => {
    loading.value = true
    error.value = null

    try {
      const result = await fetcher()
      data.value = result
      return result
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    data,
    loading,
    error,
    run,
  }
}