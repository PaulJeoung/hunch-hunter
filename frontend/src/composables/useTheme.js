import { ref, onMounted } from 'vue'

const isDark = ref(true)

export function useTheme() {
  const applyTheme = (dark) => {
    isDark.value = dark
    if (dark) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  const toggleTheme = () => {
    applyTheme(!isDark.value)
  }

  onMounted(() => {
    const saved = localStorage.getItem('theme')
    if (saved === 'light') {
      applyTheme(false)
    } else {
      applyTheme(true)
    }
  })

  return { isDark, toggleTheme }
}