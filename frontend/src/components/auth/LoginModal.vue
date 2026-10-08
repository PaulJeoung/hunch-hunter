<template>
  <div 
    v-if="isOpen" 
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm touch-none select-none"
    @touchmove.prevent
    @wheel.prevent
  >
    <div 
      class="w-full max-w-sm bg-zinc-900 border-2 border-zinc-700 shadow-[4px_4px_0px_0px_#18181b] p-6 relative font-dot text-zinc-100"
      @click.stop
    >
      <!-- 닫기 버튼 -->
      <button 
        @click="handleClose" 
        class="absolute top-4 right-4 text-zinc-400 hover:text-zinc-100 text-lg"
      >
        <i class="bi bi-x-lg"></i>
      </button>

      <div class="mb-5 text-center">
        <h3 class="text-lg font-black tracking-wider text-emerald-400 flex items-center justify-center gap-2">
          <i class="bi bi-shield-lock-fill"></i> HUNCH HUNTER LOGIN
        </h3>
        <p class="text-xs text-zinc-400 mt-1">KOSPI & KOSDAQ RAIDER</p>
      </div>

      <form @submit.prevent="submitLogin" class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-zinc-300 mb-1">이메일 (ID)</label>
          <input 
            v-model="email" 
            type="email" 
            required 
            autocomplete="email"
            placeholder="test@test.com"
            class="w-full px-3 py-2 text-sm bg-zinc-950 border border-zinc-700 focus:border-emerald-400 focus:outline-none text-zinc-100 font-mono"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-zinc-300 mb-1">비밀번호 (PW)</label>
          <input 
            v-model="password" 
            type="password" 
            required 
            autocomplete="current-password"
            placeholder="••••••••"
            class="w-full px-3 py-2 text-sm bg-zinc-950 border border-zinc-700 focus:border-emerald-400 focus:outline-none text-zinc-100 font-mono"
          />
        </div>

        <!-- 🔒 시큐어 코딩: PW는 저장하지 않고 ID(이메일)만 기억 -->
        <div class="flex items-center gap-2 py-1">
          <input 
            id="rememberId" 
            v-model="rememberId" 
            type="checkbox" 
            class="w-4 h-4 accent-emerald-500 rounded cursor-pointer"
          />
          <label for="rememberId" class="text-xs text-zinc-300 cursor-pointer">
            아이디(이메일) 저장
          </label>
        </div>

        <button 
          type="submit" 
          :disabled="isSubmitting"
          class="w-full py-2.5 bg-emerald-400 hover:bg-emerald-300 disabled:opacity-50 text-zinc-950 font-black text-sm border-2 border-zinc-950 transition"
        >
          {{ isSubmitting ? '로그인 처리 중...' : 'LOGIN' }}
        </button>
      </form>

      <!-- 간편 소셜 로그인 확장 영역 -->
      <!-- <div class="mt-6 pt-5 border-t border-zinc-800">
        <p class="text-[11px] text-zinc-400 text-center mb-3">간편 소셜 로그인 (연동 지원)</p>
        <div class="grid grid-cols-3 gap-2">
          <button 
            type="button" 
            @click="onOAuthClick('google')"
            class="py-1.5 px-2 bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-xs font-bold flex items-center justify-center gap-1.5 transition"
          >
            <i class="bi bi-google text-red-400"></i> Google
          </button>
          
          <button 
            type="button" 
            @click="onOAuthClick('kakao')"
            class="py-1.5 px-2 bg-[#FEE500] hover:bg-[#FDD835] text-zinc-900 border border-zinc-700 text-xs font-bold flex items-center justify-center gap-1.5 transition"
          >
            <i class="bi bi-chat-fill text-zinc-900"></i> Kakao
          </button>

          <button 
            type="button" 
            @click="onOAuthClick('naver')"
            class="py-1.5 px-2 bg-[#03C75A] hover:bg-[#02b351] text-white border border-zinc-700 text-xs font-bold flex items-center justify-center gap-1.5 transition"
          >
            <span class="font-black text-xs">N</span> Naver
          </button>
        </div>
      </div> -->
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  isOpen: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'submit', 'oauth'])

const email = ref('')
const password = ref('')
const rememberId = ref(false)
const isSubmitting = ref(false)

// 🔒 보안 준수: 저장 키를 분리하고 오직 이메일만 보관
const STORAGE_EMAIL_KEY = 'hh_remembered_email'

onMounted(() => {
  const savedEmail = localStorage.getItem(STORAGE_EMAIL_KEY)
  if (savedEmail) {
    email.value = savedEmail
    rememberId.value = true
  }
})

// 모달 활성화 시 배경 제스처/스크롤 봉쇄
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
    password.value = '' // 모달 닫힐 때 메모리의 PW 필드 즉시 파기
  }
})

const handleClose = () => {
  emit('close')
}

const submitLogin = async () => {
  // 이메일 형식 검증 (RFC 5322 간이 정규식)
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value.trim())) {
    alert('올바른 이메일 형식을 입력해 주세요.')
    return
  }

  isSubmitting.value = true

  // 아이디 저장 로직 (비밀번호는 절대 저장 금지)
  if (rememberId.value) {
    localStorage.setItem(STORAGE_EMAIL_KEY, email.value.trim())
  } else {
    localStorage.removeItem(STORAGE_EMAIL_KEY)
  }

  try {
    await emit('submit', { email: email.value, password: password.value })
  } finally {
    // 메모리에 남은 PW 즉시 초기화
    password.value = ''
    isSubmitting.value = false
  }
}

const onOAuthClick = (provider) => {
  emit('oauth', provider)
}
</script>