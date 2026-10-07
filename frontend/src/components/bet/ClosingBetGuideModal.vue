<template>
  <teleport to="body">
    <div 
      v-if="isOpen" 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 font-dot"
      @click.self="$emit('close')"
    >
      <div class="border-2 border-zinc-900 dark:border-zinc-700 bg-white dark:bg-zinc-950 max-w-lg w-full shadow-[8px_8px_0px_0px_#18181b] dark:shadow-[8px_8px_0px_0px_#000000]">
        <!-- 레트로 윈도우 타이틀바 -->
        <div class="bg-amber-500 text-zinc-950 px-3 py-1.5 flex justify-between items-center text-xs font-black">
          <span class="flex items-center gap-1.5">
            <i class="bi bi-lightning-charge-fill"></i> CLOSING_BET_STRATEGY_MANUAL.txt
          </span>
          <button @click="$emit('close')" class="hover:text-red-700 font-mono">[X]</button>
        </div>

        <div class="p-4 space-y-3 text-xs leading-relaxed max-h-[70vh] overflow-y-auto">
          <div class="border border-zinc-300 dark:border-zinc-800 p-3 bg-zinc-50 dark:bg-zinc-900/40">
            <span class="font-bold text-amber-600 dark:text-amber-400 block mb-1">
              <i class="bi bi-lightning-fill mr-1"></i>단기 종가 배팅 매매란?
            </span>
            <p class="text-zinc-600 dark:text-zinc-400">
              장 마감 직전(15:15~15:20) 시장가 체결 강도와 거래량 추세를 스캔해, 다음 날 시초가 및 단기 급등 변곡점을 공략하는 전략입니다[cite: 2].
            </p>
          </div>

          <div class="border border-zinc-300 dark:border-zinc-800 p-3 bg-zinc-50 dark:bg-zinc-900/40">
            <span class="font-bold text-emerald-600 dark:text-emerald-400 block mb-1">
              <i class="bi bi-speedometer2 mr-1"></i>CVD 수급 강도 & OBV
            </span>
            <p class="text-zinc-600 dark:text-zinc-400">
              <strong>CVD +15% 이상</strong>은 시장가 매수 호가가 쏟아져 들어온 스마트머니의 실체결 신호이며, <strong>OBV BULL</strong>은 중단기 거래량 추세선 위에 주가가 안착한 상태를 의미합니다[cite: 2].
            </p>
          </div>

          <div class="border border-zinc-300 dark:border-zinc-800 p-3 bg-zinc-50 dark:bg-zinc-900/40">
            <span class="font-bold text-rose-600 dark:text-rose-400 block mb-1">
              <i class="bi bi-bullseye mr-1"></i>1차(+10%) / 2차(+20%) 분할 익절 규칙
            </span>
            <p class="text-zinc-600 dark:text-zinc-400">
              • <strong>1차 목표가(+10%)</strong> 도달 시 50% 분할 매도 후 잔여 물량 스탑로스를 매수가(본전)로 상향 설정합니다[cite: 2].<br>
              • <strong>2차 목표가(+20%)</strong> 도달 시 잔여 물량을 전량 청산하여 수익을 극대화합니다[cite: 2].
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