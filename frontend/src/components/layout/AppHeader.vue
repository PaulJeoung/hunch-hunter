<template>
  <header class="border-b-2 border-zinc-900 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-3 sm:px-4 h-14 flex items-center justify-between">
      <!-- 로고 및 서비스 명 -->
      <div class="flex items-center space-x-2 sm:space-x-3">
        <div class="w-8 h-8 border-2 border-zinc-900 dark:border-emerald-400 bg-emerald-400 dark:bg-emerald-500 text-zinc-950 font-black flex items-center justify-center text-base shadow-[2px_2px_0px_0px_#18181b] dark:shadow-[2px_2px_0px_0px_#34d399]">
          <i class="bi bi-crosshair2"></i>
        </div>
        <div class="flex items-baseline gap-1.5 sm:gap-2">
          <span class="text-base sm:text-lg font-black tracking-wider text-zinc-900 dark:text-emerald-400">
            HUNCH HUNTER
          </span>
          <span class="hidden sm:inline-block text-[10px] px-1 py-0.5 border border-zinc-900 dark:border-zinc-700 bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-mono">
            v1.1.0
          </span>
        </div>
      </div>

      <!-- 우측 컨트롤 버튼 (테마 토글 & 로그인) -->
      <div class="flex items-center gap-2 sm:gap-3">
        <!-- 다크/라이트 모드 버튼 -->
        <button 
          @click="toggleTheme" 
          class="dot-btn bg-zinc-100 dark:bg-zinc-900 text-zinc-800 dark:text-zinc-200"
          title="테마 전환"
        >
          <i :class="isDark ? 'bi bi-sun-fill text-amber-500' : 'bi bi-moon-stars-fill text-indigo-500'"></i>
          <span class="text-xs">{{ isDark ? 'LIGHT' : 'DARK' }}</span>
        </button>

        <button 
          v-if="!user" 
          @click="$emit('login')" 
          class="dot-btn bg-emerald-400 hover:bg-emerald-300 text-zinc-950 font-bold"
        >
          <i class="bi bi-box-arrow-in-right"></i>
          <span>LOGIN</span>
        </button>
        <div v-else class="flex items-center gap-1.5 sm:gap-2 text-xs">
          <span class="hidden md:inline-block border border-zinc-400 dark:border-zinc-700 px-2 py-1 bg-zinc-200 dark:bg-zinc-900 font-mono text-zinc-700 dark:text-zinc-300">
            <i class="bi bi-person-fill mr-1"></i>{{ user.email }}
          </span>
          <button 
            @click="$emit('logout')" 
            class="dot-btn bg-rose-500 hover:bg-rose-400 text-white"
            title="로그아웃"
          >
            <i class="bi bi-power"></i>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useTheme } from '../../composables/useTheme'

const { isDark, toggleTheme } = useTheme()

defineProps({
  user: { type: Object, default: null }
})
defineEmits(['login', 'logout'])
</script>