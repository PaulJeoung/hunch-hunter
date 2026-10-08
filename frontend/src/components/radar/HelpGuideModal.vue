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
            <i class="bi bi-radar"></i> 세력 매트릭스 포착 전략
          </span>
          <button @click="$emit('close')" class="hover:text-red-400 font-mono">[X]</button>
        </div>

        <div class="p-4 space-y-3.5 text-xs leading-relaxed max-h-[75vh] overflow-y-auto">
          <!-- 1. 초보자 한눈 요약 -->
          <div class="border-2 border-emerald-500/50 p-3 bg-emerald-50/50 dark:bg-emerald-950/20">
            <span class="font-bold text-emerald-700 dark:text-emerald-400 block mb-1">
              <i class="bi bi-info-circle-fill mr-1"></i>Shadow Tracking 방식은?
            </span>
            <p class="text-zinc-700 dark:text-zinc-300">
              호재 뉴스가 뜨기 전, 외국인과 기관(스마트머니)이 <strong>주가를 크게 띄우지 않고 티 안 나게 물량을 모아가는 길목 종목</strong>을 알고리즘으로 발굴하는 화면입니다.
            </p>
          </div>

          <!-- 2. 표에서 어떤 숫자를 확인해야 하나요? -->
          <div class="border border-zinc-300 dark:border-zinc-800 p-3 bg-zinc-50 dark:bg-zinc-900/40 space-y-2.5">
            <span class="font-bold text-zinc-900 dark:text-zinc-100 block border-b border-zinc-200 dark:border-zinc-800 pb-1">
              <i class="bi bi-check2-circle mr-1 text-emerald-500"></i>화면의 핵심 수치 읽는 법
            </span>

            <!-- 외인/기관 순매수 -->
            <div class="pl-2 border-l-2 border-amber-500 space-y-0.5">
              <p class="text-zinc-800 dark:text-zinc-200 font-semibold">
                1. 외인 / 기관 순매수 (+빨강 / -파랑)
              </p>
              <p class="text-zinc-600 dark:text-zinc-400">
                개인은 매도하고, 외인과 기관이 <strong class="text-rose-500">+빨간색(순매수)</strong>으로 적극 담았는지 확인하세요. <span class="text-blue-500">-파란색</span>은 물량을 던진 상태를 의미합니다.
              </p>
            </div>

            <!-- 거래량 이상치 -->
            <div class="pl-2 border-l-2 border-emerald-500 space-y-0.5">
              <p class="text-zinc-800 dark:text-zinc-200 font-semibold">
                2. 거래량 이상치 (VOL Z-SCORE)
              </p>
              <p class="text-zinc-600 dark:text-zinc-400">
                평소 60일 평균 거래량 대비 통계적 폭증 강도입니다. <strong>+1.2σ 이상</strong>일 때 세력의 강력한 자금 유입이 시작된 것으로 해석합니다.
              </p>
            </div>

            <!-- 5일 연속성 -->
            <div class="pl-2 border-l-2 border-cyan-500 space-y-0.5">
              <p class="text-zinc-800 dark:text-zinc-200 font-semibold">
                3. 5일 연속성 (지속 점수)
              </p>
              <p class="text-zinc-600 dark:text-zinc-400">
                하루 반짝 산 것이 아니라, <strong>최근 5일간 꾸준히 매집을 이어왔는지</strong>를 나타냅니다. 연속 점수가 높을수록 세력의 진입 의지가 탄탄합니다.
              </p>
            </div>

            <!-- 매집 점수 -->
            <div class="pl-2 border-l-2 border-purple-500 space-y-0.5">
              <p class="text-zinc-800 dark:text-zinc-200 font-semibold">
                4. 종합 매집 점수 (SCORE)
              </p>
              <p class="text-zinc-600 dark:text-zinc-400">
                거래량 급증도 + 순매수 규모 + 가격 압축도 등을 결합한 100점 만점 수치로, 점수가 높을수록 우선 검토 대상입니다.
              </p>
            </div>
          </div>

          <!-- 3. 초보자 실전 주의사항: [과열주의] 배지 -->
          <div class="border border-zinc-300 dark:border-zinc-800 p-3 bg-zinc-50 dark:bg-zinc-900/40">
            <span class="font-bold text-rose-600 dark:text-rose-400 block mb-1">
              <i class="bi bi-exclamation-triangle-fill mr-1"></i>[과열주의] 배지가 붙은 종목 주의
            </span>
            <p class="text-zinc-600 dark:text-zinc-400">
              최근 5일 이내 상한가(급등) 이력이 있는 종목에 표시됩니다. 단기 차익 실현 물량이 쏟아지며 급락할 위험이 있으니 <strong>초보자는 과열 배지가 없는 조용한 구간의 종목을 우선 공략</strong>하세요.
            </p>
          </div>

          <!-- 4. 실전 TIP -->
          <div class="border border-dashed border-zinc-400 dark:border-zinc-700 p-2.5 text-zinc-500 dark:text-zinc-400 bg-zinc-100/50 dark:bg-zinc-900/30">
            <i class="bi bi-cursor-fill mr-1 text-emerald-500"></i>
            <strong>실전 TIP:</strong> 종목명을 클릭하면 <strong>토스증권 호가 및 주문 화면</strong>으로 새 창 연결되어 현재 호가창 상황을 바로 확인할 수 있습니다.
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