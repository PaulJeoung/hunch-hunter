<template>
  <div>
    <!-- 테이블 스크롤 영역 (max-h-[300px]) -->
    <div class="overflow-x-auto max-h-[300px] border border-zinc-300 dark:border-zinc-800">
      <table class="w-full text-left text-xs font-mono border-collapse">
        <thead class="sticky top-0 z-10 bg-zinc-200 dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300">
          <tr class="border-b-2 border-zinc-900 dark:border-zinc-700">
            <th class="dot-th min-w-[130px]">종목명</th>
            <th class="dot-th min-w-[85px]">현재가</th>
            <th class="dot-th min-w-[70px]">등락률</th>
            <th class="dot-th min-w-[170px]">5일 포착 이력 (뱃지)</th>
            <th class="dot-th min-w-[85px] text-center">총 노출일</th>
            <th class="dot-th min-w-[75px] text-center">당일 상태</th>
            <th class="dot-th min-w-[75px] text-right">복합 점수</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-zinc-200 dark:divide-zinc-800">
          <tr v-for="item in overlapData?.data" :key="item.ticker" class="dot-tr">
            <!-- 종목명 및 토스 링크 -->
            <td class="py-2.5 px-3 font-sans font-bold truncate">
              <a 
                :href="getTossUrl(item.ticker)" 
                target="_blank" 
                rel="noopener noreferrer"
                class="text-zinc-900 dark:text-zinc-100 hover:text-blue-600 dark:hover:text-blue-400 hover:underline inline-flex items-center gap-1 group"
                title="토스증권 시세 조회로 이동"
              >
                <span>{{ item.name }}</span>
                <i class="bi bi-box-arrow-up-right text-[10px] opacity-40 group-hover:opacity-100"></i>
              </a>
            </td>

            <!-- 가격 및 등락률 -->
            <td class="py-2.5 px-3 text-zinc-800 dark:text-zinc-200">{{ item.close_price?.toLocaleString() }}원</td>
            <td class="py-2.5 px-3 font-bold" :class="item.day_return >= 0 ? 'text-red-500' : 'text-blue-500'">
              {{ item.day_return > 0 ? '+' : '' }}{{ item.day_return }}%
            </td>

            <!-- 5일 포착 이력 뱃지 -->
            <td class="py-2.5 px-3">
              <div class="flex items-center gap-1.5 flex-wrap">
                <!-- 양쪽 모두 포착 시 CROSS 뱃지 -->
                <span 
                  v-if="item.is_cross_matched" 
                  class="px-1.5 py-0.5 text-[10px] font-black border border-purple-500/40 bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300"
                  title="5일 내 세력매집 & 종가배팅 모두 포착"
                >
                  <i class="bi bi-intersect mr-0.5"></i>CROSS
                </span>

                <!-- 세력매집 노출 일수 뱃지 (2회 이상 시 강조) -->
                <span 
                  v-if="item.acc_days > 0"
                  class="px-1.5 py-0.5 text-[10px] font-bold border"
                  :class="item.is_acc_repeat 
                    ? 'border-emerald-500 bg-emerald-100 text-emerald-900 dark:bg-emerald-950 dark:text-emerald-300 font-black' 
                    : 'border-zinc-300 dark:border-zinc-700 bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'"
                >
                  매집 {{ item.acc_days }}일
                </span>

                <!-- 종가배팅 노출 일수 뱃지 (2회 이상 시 강조) -->
                <span 
                  v-if="item.bet_days > 0"
                  class="px-1.5 py-0.5 text-[10px] font-bold border"
                  :class="item.is_bet_repeat 
                    ? 'border-amber-500 bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-300 font-black' 
                    : 'border-zinc-300 dark:border-zinc-700 bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400'"
                >
                  종배 {{ item.bet_days }}일
                </span>
              </div>
            </td>

            <!-- 총 노출일 -->
            <td class="py-2.5 px-3 text-center">
              <span class="px-2 py-0.5 text-[11px] font-bold border border-indigo-400/30 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300">
                {{ item.total_days }}일간
              </span>
            </td>

            <!-- 당일 상태 -->
            <td class="py-2.5 px-3 text-center">
              <span 
                v-if="item.is_today" 
                class="px-1.5 py-0.5 text-[10px] bg-rose-500 text-white font-bold animate-pulse"
              >
                오늘 포착
              </span>
              <span v-else class="text-[10px] text-zinc-400 font-mono">
                유지 구간
              </span>
            </td>

            <!-- 복합 점수 -->
            <td class="py-2.5 px-3 text-right font-black text-rose-600 dark:text-rose-400">
              {{ item.composite_score }}점
            </td>
          </tr>

          <!-- 빈 데이터 안내 -->
          <tr v-if="!overlapData?.data || overlapData?.data.length === 0">
            <td colspan="7" class="py-8 text-center text-zinc-400 font-mono">
              [!] 5일 내 2회 이상 연속 포착되거나 두 알고리즘에 교차 포착된 종목이 없습니다.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- PRO 플랜 게이트 배너 -->
    <div v-if="overlapData?.is_truncated" class="mt-3 p-2.5 border-2 border-zinc-900 dark:border-zinc-700 bg-zinc-100 dark:bg-zinc-900 text-center text-xs font-mono">
      <i class="bi bi-lock-fill mr-1 text-amber-500"></i>
      PRO 구독 시 5일 중복 분석 전체 종목({{ overlapData.total_count }}개)을 모두 열람하실 수 있습니다.
    </div>
  </div>
</template>

<script setup>
defineProps({
  overlapData: { type: Object, default: () => null }
})

// 토스증권 상세 주문 URL
const getTossUrl = (ticker) => {
  if (!ticker) return '#'
  const cleanTicker = String(ticker).replace(/^A/, '').padStart(6, '0')
  return `https://www.tossinvest.com/stocks/A${cleanTicker}/order`
}
</script>