<template>
  <teleport to="body">
    <div 
      v-if="isOpen" 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 font-dot"
      @click.self="$emit('close')"
    >
      <div class="border-2 border-zinc-900 dark:border-zinc-700 bg-white dark:bg-zinc-950 max-w-md w-full shadow-[8px_8px_0px_0px_#18181b] dark:shadow-[8px_8px_0px_0px_#000000]">
        <!-- 상단 레트로 윈도우 타이틀바 -->
        <div class="bg-emerald-400 text-zinc-950 px-3 py-1.5 flex justify-between items-center text-xs font-black">
          <span class="flex items-center gap-1.5">
            <i class="bi bi-shield-shaded"></i> MEMBERSHIP
          </span>
          <button @click="$emit('close')" class="hover:text-red-700 font-mono">[X]</button>
        </div>

        <!-- 모달 내용 -->
        <div class="p-4 space-y-3 text-xs leading-relaxed max-h-[75vh] overflow-y-auto">
          <!-- 비로그인 (GUEST) -->
          <div class="border border-zinc-300 dark:border-zinc-800 p-2.5 bg-zinc-50 dark:bg-zinc-900/40">
            <div class="flex items-center justify-between mb-1">
              <span class="font-bold text-zinc-700 dark:text-zinc-300">
                <i class="bi bi-person mr-1"></i>비로그인 (GUEST)
              </span>
              <span class="px-1.5 py-0.2 border border-zinc-400 text-[10px] font-mono text-zinc-500">방문자</span>
            </div>
            <p class="text-zinc-600 dark:text-zinc-400">
              • 실시간 거래대금 TOP 50, 급등·급락·시총 TOP 10 등 <strong>공개 시장 지표 무료 열람</strong><br>
              • 세력 매집 흔적 / 단기 종가 배팅 시그널은 잠금(비공개) 상태입니다.
            </p>
          </div>

          <!-- FREE 등급 -->
          <div class="border border-zinc-300 dark:border-zinc-800 p-2.5 bg-zinc-50 dark:bg-zinc-900/40">
            <div class="flex items-center justify-between mb-1">
              <span class="font-bold text-blue-600 dark:text-blue-400">
                <i class="bi bi-person-check-fill mr-1"></i>일반 회원 (FREE)
              </span>
              <span class="px-1.5 py-0.2 border border-blue-400 text-[10px] font-mono text-blue-600 dark:text-blue-400">가입 즉시</span>
            </div>
            <p class="text-zinc-600 dark:text-zinc-400">
              • 세력 매집 흔적 및 단기 종가 배팅 시그널 <strong>1개 종목 맛보기 열람</strong><br>
              • 이메일 가입 즉시 자동으로 부여되는 기본 등급입니다.
            </p>
          </div>

          <!-- PRO 승인 대기 (PENDING) -->
          <div class="border border-amber-300 dark:border-amber-900/60 p-2.5 bg-amber-50/60 dark:bg-amber-950/20">
            <div class="flex items-center justify-between mb-1">
              <span class="font-bold text-amber-700 dark:text-amber-400">
                <i class="bi bi-hourglass-split mr-1"></i>PRO 신청 대기 (PENDING / DEACTIVE)
              </span>
              <span class="px-1.5 py-0.2 border border-amber-500 text-[10px] font-mono text-amber-700 dark:text-amber-400">승인 심사</span>
            </div>
            <p class="text-zinc-600 dark:text-zinc-400">
              • PRO 신청 후 <strong>관리자 승인 전 상태</strong>로, 시그널 <strong>상위 3개 종목만 제한 열람</strong><br>
              • 관리자가 확인 후 승인(ACTIVE) 처리 시 PRO 전체 열람으로 자동 전환됩니다.
            </p>
          </div>

          <!-- PRO (유료/승인 완료) -->
          <div class="border-2 border-emerald-500/60 p-2.5 bg-emerald-50/50 dark:bg-emerald-950/20">
            <div class="flex items-center justify-between mb-1">
              <span class="font-bold text-emerald-700 dark:text-emerald-400">
                <i class="bi bi-shield-shaded mr-1"></i>정규 회원 (PRO)
              </span>
              <span class="px-1.5 py-0.2 bg-emerald-500 text-zinc-950 font-black text-[10px] font-mono">ALL PASS</span>
            </div>
            <p class="text-zinc-700 dark:text-zinc-300">
              • <strong>당일 발굴된 전체 매집 시그널 & 종가 배팅 종목 무제한 열람</strong><br>
              • 실시간 호가/CVD/OBV 정밀 수급 데이터 및 목표가 지표 전체 공개
            </p>
          </div>

          <!-- ADMIN (최고 관리자) -->
          <!-- <div class="border border-purple-300 dark:border-purple-900/60 p-2.5 bg-purple-50/50 dark:bg-purple-950/20">
            <div class="flex items-center justify-between mb-1">
              <span class="font-bold text-purple-700 dark:text-purple-400">
                <i class="bi bi-stars mr-1"></i>관리자 (ADMIN)
              </span>
              <span class="px-1.5 py-0.2 border border-purple-500 text-[10px] font-mono text-purple-700 dark:text-purple-400">MASTER</span>
            </div>
            <p class="text-zinc-600 dark:text-zinc-400">
              • 모든 시그널 제한 해제 및 사용자 등급 관리 권한
            </p>
          </div> -->
        </div>

        <!-- 하단 닫기 버튼 -->
        <div class="p-3 border-t-2 border-zinc-900 dark:border-zinc-800 flex justify-end bg-zinc-50 dark:bg-zinc-900">
          <button @click="$emit('close')" class="dot-btn bg-zinc-900 text-white dark:bg-zinc-200 dark:text-zinc-900 text-xs">
            [ENTER] 닫기
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
defineProps({
  isOpen: { type: Boolean, default: false }
})
defineEmits(['close'])
</script>