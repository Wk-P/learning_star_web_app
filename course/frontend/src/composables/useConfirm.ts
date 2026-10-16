import { ref } from 'vue'

interface ConfirmOptions {
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  type?: 'danger' | 'warning' | 'info'
}

interface ConfirmState extends ConfirmOptions {
  visible: boolean
  resolve: ((v: boolean) => void) | null
}

export const confirmState = ref<ConfirmState>({
  visible: false,
  message: '',
  resolve: null,
})

export function useConfirm() {
  function confirm(options: ConfirmOptions | string): Promise<boolean> {
    const opts = typeof options === 'string' ? { message: options } : options
    return new Promise(resolve => {
      confirmState.value = {
        visible: true,
        title: opts.title ?? '确认操作',
        message: opts.message,
        confirmText: opts.confirmText ?? '确认',
        cancelText: opts.cancelText ?? '取消',
        type: opts.type ?? 'info',
        resolve,
      }
    })
  }

  function close(result: boolean) {
    confirmState.value.resolve?.(result)
    confirmState.value.visible = false
  }

  return { confirm, close }
}
