<template>
  <teleport to="body">
    <div 
      v-if="isOpen" 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 font-dot"
      @click.self="$emit('close')"
    >
      <div class="border-2 border-zinc-900 dark:border-zinc-700 bg-white dark:bg-zinc-950 max-w-lg w-full shadow-[8px_8px_0px_0px_#18181b] dark:shadow-[8px_8px_0px_0px_#000000]">
        <!-- 레트로 윈도우 타이틀바 -->
        <div class="bg-zinc-900 dark:bg-zinc-800 text-white px-3 py-1.5 flex justify-between items-center text-xs font-bold">
          <span class="flex items-center gap-1.5">
            <i class="bi bi-terminal"></i> HUNCH_METRICS_MANUAL.txt
          </span>
          <button @click="$emit('close')" class="hover:text-red-400 font-mono">[X]</button>
        </div>

        <div class="p-4 space-y-3 text-xs leading-relaxed max-h-[70vh] overflow-y-auto">
          <div class="border border-zinc-300 dark:border-zinc-800 p-3 bg-zinc-50 dark:bg-zinc-900/40">
            <span class="font-bold text-emerald-600 dark:text-emerald-400 block mb-1">
              <i class="bi bi-graph-up-arrow mr-1"></i>거래량 이상치 (Z-Score)
            </span>
            <p class="text-zinc-600 dark:text-zinc-400">
              60일 평균 거래량 대비 통계적 돌출 강도입니다. +1.2σ 이상일 때 스마트머니 유입으로 판단합니다.
            </p>
          </div>

          <div class="border border-zinc-300 dark:border-zinc-800 p-3 bg-zinc-50 dark:bg-zinc-900/40">
            <span class="font-bold text-amber-600 dark:text-amber-400 block mb-1">
              <i class="bi bi-activity mr-1"></i>수급 강도 (CVD Ratio)
            </span>
            <p class="text-zinc-600 dark:text-zinc-400">
              호가창 시장가 순매수 체결 강도입니다. +15% 이상일수록 공격적인 물량 흡수를 의미합니다.
            </p>
          </div>

          <div class="border border-zinc-300 dark:border-zinc-800 p-3 bg-zinc-50 dark:bg-zinc-900/40">
            <span class="font-bold text-blue-600 dark:text-blue-400 block mb-1">
              <i class="bi bi-compass mr-1"></i>OBV 추세 상태
            </span>
            <p class="text-zinc-600 dark:text-zinc-400">
              누적 거래량 선행 지표가 20일 시그널선 위에 머무르는 강세(BULL) 구간을 포착합니다.
            </p>
          </div>
        </div>

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