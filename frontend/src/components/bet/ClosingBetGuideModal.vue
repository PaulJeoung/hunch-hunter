<template>
  <teleport to="body">
    <div 
      v-if="isOpen" 
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 font-dot"
      @click.self="$emit('close')"
    >
      <div class="border-2 border-zinc-900 dark:border-zinc-700 bg-white dark:bg-zinc-950 max-w-lg w-full shadow-[8px_8px_0px_0px_#18181b] dark:shadow-[8px_8px_0px_0px_#000000]">
        <!-- 상단 타이틀바 -->
        <div class="bg-amber-500 text-zinc-950 px-3 py-1.5 flex justify-between items-center text-xs font-black">
          <span class="flex items-center gap-1.5">
            <i class="bi bi-lightning-charge-fill"></i> 종가 배팅 전략
          </span>
          <button @click="$emit('close')" class="hover:text-red-700 font-mono">[X]</button>
        </div>

        <div class="p-4 space-y-3.5 text-xs leading-relaxed max-h-[75vh] overflow-y-auto">
          <!-- 1. 초보자 한 줄 요약 -->
          <div class="border-2 border-amber-500/50 p-3 bg-amber-50/50 dark:bg-amber-950/20">
            <span class="font-bold text-amber-700 dark:text-amber-400 block mb-1">
              <i class="bi bi-info-circle-fill mr-1"></i> 종가 배팅 이란?
            </span>
            <p class="text-zinc-700 dark:text-zinc-300">
              장 마감 직전(15:15~15:20) 큰손들의 매수 흔적이 집중된 종목을 매수하여, <strong>다음 날 아침 시초가 갭상승 또는 장중 급등 시 빠르게 차익을 실현</strong>하는 단기 매매 기법입니다.
            </p>
          </div>

          <!-- 2. 화면에서 꼭 봐야 할 핵심 지표 2가지 -->
          <div class="border border-zinc-300 dark:border-zinc-800 p-3 bg-zinc-50 dark:bg-zinc-900/40 space-y-2">
            <span class="font-bold text-emerald-600 dark:text-emerald-400 block">
              <i class="bi bi-search mr-1"></i>표에서 어떤 숫자를 확인해야 하나요?
            </span>
            
            <div class="pl-2 border-l-2 border-emerald-500 space-y-1">
              <p class="text-zinc-800 dark:text-zinc-200 font-semibold">
                1. 수급 강도 (CVD): 큰손이 공격적으로 매수한 비율
              </p>
              <p class="text-zinc-600 dark:text-zinc-400">
                수치가 <strong>+15% 이상</strong>이면 매도 호가를 위로 긁으며 공격적으로 물량을 흡수한 스마트머니 유입 신호입니다.
              </p>
            </div>

            <div class="pl-2 border-l-2 border-blue-500 space-y-1">
              <p class="text-zinc-800 dark:text-zinc-200 font-semibold">
                2. OBV 상태: 거래량 에너지 추세
              </p>
              <p class="text-zinc-600 dark:text-zinc-400">
                <strong>BULL(강세)</strong> 표시는 거래량 선행 지표가 20일 추세선 위에 위치하여 추가 상승 여력이 충분한 상태를 뜻합니다.
              </p>
            </div>
          </div>

          <!-- 3. 원금 보존을 위한 분할 익절 및 손절 규칙 -->
          <div class="border border-zinc-300 dark:border-zinc-800 p-3 bg-zinc-50 dark:bg-zinc-900/40">
            <span class="font-bold text-rose-600 dark:text-rose-400 block mb-1">
              <i class="bi bi-shield-check mr-1"></i>초보자 원금 보호 매매 원칙
            </span>
            <ul class="text-zinc-600 dark:text-zinc-400 space-y-1.5 list-disc list-inside">
              <li>
                <strong>1차 목표가(+10%) 도달 시:</strong> 보유 물량의 <strong>50%를 먼저 익절</strong>하여 수익을 챙기고, 나머지 물량의 매도가는 본전(매수가)으로 걸어둡니다.
              </li>
              <li>
                <strong>2차 목표가(+20%) 도달 시:</strong> 남은 물량을 전량 매도하여 수익을 극대화합니다.
              </li>
              <li>
                <strong>손절선 관리:</strong> 예상과 다르게 장 시작 후 밀릴 경우 -2.5% 터치 시 과감히 정리하여 손실을 최소화합니다.
              </li>
            </ul>
          </div>

          <!-- 4. 실전 매매 팁 -->
          <div class="border border-dashed border-zinc-400 dark:border-zinc-700 p-2.5 text-zinc-500 dark:text-zinc-400 bg-zinc-100/50 dark:bg-zinc-900/30">
            <i class="bi bi-cursor-fill mr-1 text-amber-500"></i>
            <strong>실전 TIP:</strong> 종목명을 클릭하면 <strong>토스증권 상세 주문 페이지</strong>로 바로 이동하여 실시간 호가를 확인하고 주문할 수 있습니다.
          </div>
        </div>

        <!-- 하단 닫기 바 -->
        <div class="p-3 border-t-2 border-zinc-900 dark:border-zinc-800 flex justify-end bg-zinc-50 dark:bg-zinc-900">
          <button @click="$emit('close')" class="dot-btn bg-zinc-900 text-white dark:bg-zinc-200 dark:text-zinc-900 text-xs">
            [ENTER] 확인했습니다
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