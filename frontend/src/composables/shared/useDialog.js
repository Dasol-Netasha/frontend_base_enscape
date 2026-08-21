import { inject } from 'vue'

export const DIALOG_CONTEXT_KEY = Symbol('dialog-context')

// 애플리케이션 어디서든 alert/confirm/prompt를 호출하기 위한 진입점.
// DialogProvider 바깥에서 호출하면 실제 표시할 호스트가 없으므로 예외를 던진다.
export const useDialog = () => {
  const dialogContext = inject(DIALOG_CONTEXT_KEY, null)
  if (!dialogContext) {
    throw new Error('useDialog must be used within DialogProvider.')
  }

  return dialogContext
}
