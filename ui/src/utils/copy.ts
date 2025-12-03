/**
 * 复制相关工具函数
 */
import { ElMessage } from 'element-plus'

/**
 * 使用传统方法复制文本到剪贴板
 * @param text 要复制的文本
 * @returns 复制是否成功
 */
function fallbackCopyTextToClipboard(text: string): boolean {
  try {
    const textArea = document.createElement('textarea')
    textArea.value = text
    
    // 设置样式使元素不可见
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    document.body.appendChild(textArea)
    
    // 选择并复制文本
    textArea.focus()
    textArea.select()
    const successful = document.execCommand('copy')
    document.body.removeChild(textArea)
    
    return successful
  } catch (err) {
    console.error('传统复制方法失败:', err)
    return false
  }
}

/**
 * 将文本复制到剪贴板
 * @param text 要复制的文本
 * @param successMessage 复制成功后显示的消息（如果不提供，则不显示消息）
 * @returns 复制是否成功
 */
export async function copyTextToClipboard(text: string, successMessage?: string): Promise<boolean> {
  // 检查 Clipboard API 是否可用
  if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
    try {
      await navigator.clipboard.writeText(text)
      if (successMessage) {
        ElMessage.success(successMessage)
      }
      return true
    } catch (err) {
      console.error('Clipboard API 复制失败，尝试备用方法:', err)
      // 如果 Clipboard API 失败，尝试备用方法
      return fallbackMethod()
    }
  } else {
    // Clipboard API 不可用，使用备用方法
    return fallbackMethod()
  }

  // 备用复制方法
  function fallbackMethod(): boolean {
    const result = fallbackCopyTextToClipboard(text)
    if (result) {
      if (successMessage) {
        ElMessage.success(successMessage)
      }
      return true
    } else {
      ElMessage.error('复制到剪贴板失败')
      return false
    }
  }
} 