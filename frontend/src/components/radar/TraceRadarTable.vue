<template>
  <div>
    <!-- 약 6~7개 행 표시 후 내부 스크롤 (max-h-[300px]) -->
    <div class="overflow-x-auto max-h-[300px] border border-zinc-300 dark:border-zinc-800">
      <table class="w-full text-left text-xs font-mono border-collapse">
        <thead class="sticky top-0 z-10 bg-zinc-200 dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300">
          <tr class="border-b-2 border-zinc-900 dark:border-zinc-700">
            <th class="dot-th min-w-[130px]">종목명</th>
            <th class="dot-th min-w-[85px]">종가</th>
            <th class="dot-th min-w-[75px]">등락률</th>
            <th class="dot-th min-w-[95px]">거래량 이상치(Z)</th>
            <th class="dot-th min-w-[90px]">외인 순매수</th>
            <th class="dot-th min-w-[90px]">기관 순매수</th>
            <th class="dot-th min-w-[90px] text-center">5일 연속성</th>
            <th class="dot-th min-w-[75px] text-right">매집 점수</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-zinc-200 dark:divide-zinc-800">
          <tr v-for="item in radarData?.data" :key="item.ticker" class="dot-tr">
            <td class="py-2.5 px-3 font-sans font-bold truncate">
              <div class="flex items-center gap-1.5">
                <!-- 토스증권 상세 주문 URL 링크 -->
                <a 
                  :href="getTossUrl(item.ticker)" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  class="text-zinc-900 dark:text-zinc-100 hover:text-blue-600 dark:hover:text-blue-400 hover:underline inline-flex items-center gap-1 group"
                  title="토스증권 시세 조회로 이동"
                >
                  <span>{{ item.stocks?.name || item.ticker }}</span>
                  <i class="bi bi-box-arrow-up-right text-[10px] opacity-40 group-hover:opacity-100"></i>
                </a>

                <!-- 최근 5일 내 상한가 발생 시 과열 주의 배지 표시 -->
                <span 
                  v-if="item.limit_up_count_5d > 0" 
                  class="px-1 py-0.5 text-[9px] bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30 rounded font-sans"
                  title="최근 5일 이내 상한가 이력이 있어 단기 조정 가능성이 높습니다."
                >
                  과열주의
                </span>
              </div>
            </td>
            <td class="py-2.5 px-3 text-zinc-800 dark:text-zinc-200">{{ item.close_price?.toLocaleString() }}원</td>
            <td class="py-2.5 px-3 font-bold" :class="item.day_return >= 0 ? 'text-red-500' : 'text-blue-500'">
              {{ item.day_return > 0 ? '+' : '' }}{{ item.day_return }}%
            </td>
            <td class="py-2.5 px-3 text-emerald-600 dark:text-emerald-400 font-bold">+{{ item.vol_zscore }}σ</td>
            
            <!-- 외인 순매수 -->
            <td class="py-2.5 px-3 font-semibold" :class="getAmountClass(item.foreign_net)">
              {{ formatNet(item.foreign_net) }}
            </td>

            <!-- 기관 순매수 -->
            <td class="py-2.5 px-3 font-semibold" :class="getAmountClass(item.institution_net)">
              {{ formatNet(item.institution_net) }}
            </td>

            <!-- 5일 매집 연속성 점수 -->
            <td class="py-2.5 px-3 text-center">
              <span class="px-1.5 py-0.5 rounded text-[11px] font-bold bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 border border-zinc-300 dark:border-zinc-700">
                {{ item.acc_score_5d ? item.acc_score_5d + '점' : '-' }}
              </span>
            </td>

            <!-- 종합 매집 점수 -->
            <td class="py-2.5 px-3 text-right font-black text-amber-600 dark:text-amber-400">
              {{ item.score }}점
            </td>
          </tr>
          <tr v-if="!radarData?.data || radarData?.data.length === 0">
            <td colspan="8" class="py-8 text-center text-zinc-400 font-mono">
              [!] 포착된 매집 시그널이 없습니다. 배치를 먼저 실행해 주세요.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="radarData?.is_truncated" class="mt-3 p-2.5 border-2 border-zinc-900 dark:border-zinc-700 bg-zinc-100 dark:bg-zinc-900 text-center text-xs font-mono">
      <i class="bi bi-lock-fill mr-1 text-amber-500"></i>
      PRO 구독 시 전체 발굴 종목({{ radarData.total_count }}개)을 모두 열람하실 수 있습니다.
    </div>
  </div>
</template>

<script setup>
defineProps({
  radarData: { type: Object, default: () => null }
})

// 토스증권 상세 주문 URL
const getTossUrl = (ticker) => {
  if (!ticker) return '#'
  const cleanTicker = String(ticker).replace(/^A/, '').padStart(6, '0')
  return `https://www.tossinvest.com/stocks/A${cleanTicker}/order`
}

// 부호 및 금액 단위(억) 포맷팅
const formatNet = (value) => {
  if (value === null || value === undefined) return '0.0억'
  const valInBillions = value / 100000000
  const sign = valInBillions > 0 ? '+' : ''
  return `${sign}${valInBillions.toFixed(1)}억`
}

// 텍스트 색상 클래스
const getAmountClass = (value) => {
  if (!value || value === 0) return 'text-zinc-500 dark:text-zinc-400'
  return value > 0 ? 'text-red-500 dark:text-red-400' : 'text-blue-500 dark:text-blue-400'
}
</script>