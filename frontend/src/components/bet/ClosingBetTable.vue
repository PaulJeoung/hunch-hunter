<template>
  <div>
    <!-- 약 6~7개 행 표시 후 내부 스크롤 (max-h-[300px]) -->
    <div class="overflow-x-auto max-h-[300px] border border-zinc-300 dark:border-zinc-800">
      <table class="w-full text-left text-xs font-mono border-collapse">
        <thead class="sticky top-0 z-10 bg-zinc-200 dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300">
          <tr class="border-b-2 border-zinc-900 dark:border-zinc-700">
            <th class="dot-th min-w-[110px]">종목명</th>
            <th class="dot-th min-w-[85px]">종가</th>
            <th class="dot-th min-w-[70px]">등락률</th>
            <th class="dot-th min-w-[90px]">수급강도(CVD)</th>
            <th class="dot-th min-w-[75px]">OBV</th>
            <th class="dot-th min-w-[95px] text-emerald-600 dark:text-emerald-400">1차 목표(+10%)</th>
            <th class="dot-th min-w-[95px] text-cyan-600 dark:text-cyan-400">2차 목표(+20%)</th>
            <th class="dot-th min-w-[70px] text-right">점수</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-zinc-200 dark:divide-zinc-800">
          <tr v-for="item in betData?.data" :key="item.ticker" class="dot-tr">
            <td class="py-2.5 px-3 font-sans font-bold truncate">
              <!-- 토스증권 상세 페이지 링크 -->
              <a 
                :href="getTossUrl(item.ticker)" 
                target="_blank" 
                rel="noopener noreferrer"
                class="text-zinc-900 dark:text-zinc-100 hover:text-blue-600 dark:hover:text-blue-400 hover:underline inline-flex items-center gap-1 group"
                title="토스증권 시세 조회로 이동"
              >
                <span>{{ item.stocks?.name || item.name || item.ticker }}</span>
                <i class="bi bi-box-arrow-up-right text-[10px] opacity-40 group-hover:opacity-100"></i>
              </a>
            </td>
            <td class="py-2.5 px-3 text-zinc-800 dark:text-zinc-200">{{ item.close_price?.toLocaleString() }}원</td>
            <td class="py-2.5 px-3 font-bold" :class="item.day_return >= 0 ? 'text-red-500' : 'text-blue-500'">
              {{ item.day_return > 0 ? '+' : '' }}{{ item.day_return }}%
            </td>
            <td class="py-2.5 px-3 font-bold text-amber-600 dark:text-amber-400">
              +{{ item.cvd_ratio }}%
            </td>
            <td class="py-2.5 px-3">
              <span class="px-1.5 py-0.5 border border-zinc-900 dark:border-zinc-700 bg-zinc-100 dark:bg-zinc-800 text-[10px]">
                {{ item.obv_status === 'BULL' ? '강세' : item.obv_status }}
              </span>
            </td>
            <td class="py-2.5 px-3 text-emerald-600 dark:text-emerald-400 font-bold">
              {{ item.target_price_1?.toLocaleString() }}원
            </td>
            <td class="py-2.5 px-3 text-cyan-600 dark:text-cyan-400 font-bold">
              {{ item.target_price_2?.toLocaleString() }}원
            </td>
            <td class="py-2.5 px-3 text-right font-black text-rose-600 dark:text-rose-400">
              {{ item.score }}점
            </td>
          </tr>
          <tr v-if="!betData?.data || betData?.data.length === 0">
            <td colspan="8" class="py-8 text-center text-zinc-400 font-mono">
              [!] 포착된 종가 배팅 시그널이 없습니다. 배치를 먼저 실행해 주세요.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="betData?.is_truncated" class="mt-3 p-3 border-2 border-zinc-900 dark:border-zinc-700 bg-zinc-100 dark:bg-zinc-900 text-center text-xs font-mono">
      <i class="bi bi-lock-fill mr-1 text-amber-500"></i>
      PRO 구독 시 전체 배팅 발굴 종목({{ betData.total_count }}개)을 모두 열람하실 수 있습니다.
    </div>
  </div>
</template>

<script setup>
defineProps({
  betData: { type: Object, default: () => null }
})

// 토스증권 상세 주문 URL 생성 함수
const getTossUrl = (ticker) => {
  if (!ticker) return '#'
  const cleanTicker = String(ticker).replace(/^A/, '').padStart(6, '0')
  return `https://www.tossinvest.com/stocks/A${cleanTicker}/order`
}
</script>