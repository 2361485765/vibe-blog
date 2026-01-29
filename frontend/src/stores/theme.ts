import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // 从 localStorage 读取初始值
  const savedTheme = localStorage.getItem('vibe-blog-theme')
  const isDark = ref(savedTheme === 'dark')

  // 监听变化并保存到 localStorage
  watch(isDark, (newValue) => {
    localStorage.setItem('vibe-blog-theme', newValue ? 'dark' : 'light')
  })

  const toggleTheme = () => {
    isDark.value = !isDark.value
  }

  const setDark = (value: boolean) => {
    isDark.value = value
  }

  return {
    isDark,
    toggleTheme,
    setDark
  }
})
