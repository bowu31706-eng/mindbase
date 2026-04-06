import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(false)

  function init() {
    // #ifdef H5
    document.documentElement.setAttribute('data-theme', 'light')
    // #endif
  }

  return { isDark, init }
})
