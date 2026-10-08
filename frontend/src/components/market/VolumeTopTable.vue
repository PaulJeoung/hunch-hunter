<template>
  <section class="dot-panel space-y-3">
    <div class="flex items-center justify-between border-b-2 border-zinc-900 dark:border-zinc-800 pb-3">
      <h3 class="text-sm sm:text-base font-bold text-zinc-900 dark:text-zinc-100 flex items-center gap-1.5">
        <i class="bi bi-cash-stack text-emerald-500"></i> {{ statusLabel }} 거래대금 TOP 50
      </h3>
      <span class="text-[10px] sm:text-xs text-zinc-500 font-mono">장중 외인·기관 잠정 집계</span>
    </div>

    <!-- 가로 스크롤 및 고정 높이 테이블 -->
    <div class="overflow-x-auto max-h-[500px] border border-zinc-300 dark:border-zinc-800">
      <table class="w-full text-left text-xs font-mono border-collapse">
        <thead class="sticky top-0 bg-zinc-200 dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 z-10 border-b border-zinc-900 dark:border-zinc-700">
          <tr>
            <th class="dot-th w-10 text-center">순위</th>
            <th class="dot-th min-w-[120px]">종목명</th>
            <th class="dot-th min-w-[85px]">현재가</th>
            <th class="dot-th min-w-[75px]">등락률</th>
            <th class="dot-th min-w-[95px] text-right">거래대금</th>
            <th class="dot-th min-w-[90px] text-right">시가총액</th>
            <!-- <th class="dot-th min-w-[75px] text-center">체결강도</th> -->
            <th class="dot-th min-w-[85px] text-right">외인(잠정)</th>
            <th class="dot-th min-w-[85px] text-right">기관(잠정)</th>
            <th class="dot-th min-w-[75px] text-right">개인</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-zinc-200 dark:divide-zinc-800">
          <tr v-for="(item, idx) in volumeList" :key="item.ticker" class="dot-tr">
            <td class="py-2.5 px-2 text-center text-zinc-500 font-bold">{{ idx + 1 }}</td>
            <td class="py-2.5 px-3 font-sans font-bold truncate">
              <!-- 토스증권 상세 주문 URL 링크 -->
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
            <td class="py-2.5 px-3 text-zinc-800 dark:text-zinc-200">{{ item.close?.toLocaleString() }}원</td>
            <td class="py-2.5 px-3 font-bold" :class="item.change_rate >= 0 ? 'text-red-500' : 'text-blue-500'">
              {{ item.change_rate > 0 ? '+' : '' }}{{ item.change_rate }}%
            </td>
            <!-- 거래대금 -->
            <td class="py-2.5 px-3 text-right text-zinc-800 dark:text-zinc-200 font-bold">
              {{ formatTradingValue(item.trading_value) }}
            </td>
            <!-- 시가총액 -->
            <td class="py-2.5 px-3 text-right text-zinc-600 dark:text-zinc-400 font-semibold">
              {{ formatMarketCap(item.market_cap) }}
            </td>
            <!-- 체결강도 -->
            <!-- <td class="py-2.5 px-3 text-center">
              <span 
                v-if="item.execution_strength !== null && item.execution_strength !== undefined"
                class="px-1.5 py-0.5 rounded text-[11px] font-bold"
                :class="item.execution_strength >= 100 ? 'text-red-500 dark:text-red-400 bg-red-500/10' : 'text-blue-500 dark:text-blue-400 bg-blue-500/10'"
              >
                {{ item.execution_strength }}%
              </span>
              <span v-else class="text-zinc-400">-</span>
            </td> -->
            <!-- 외국인 매수/매도 (잠정치) -->
            <td class="py-2.5 px-3 text-right font-semibold" :class="getAmountClass(item.foreign_net)">
              {{ formatNet(item.foreign_net) }}
            </td>
            <!-- 기관 매수/매도 (잠정치) -->
            <td class="py-2.5 px-3 text-right font-semibold" :class="getAmountClass(item.institution_net)">
              {{ formatNet(item.institution_net) }}
            </td>
            <!-- 개인 (장중 미집계 처리) -->
            <td class="py-2.5 px-3 text-right font-semibold" :class="getAmountClass(item.individual_net)">
              {{ item.individual_net !== null && item.individual_net !== undefined ? formatNet(item.individual_net) : '-' }}
            </td>
          </tr>
          <tr v-if="!volumeList || volumeList.length === 0">
            <td colspan="10" class="py-8 text-center text-zinc-400 font-mono">
              [!] 거래대금 데이터를 불러올 수 없습니다.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
defineProps({
  volumeList: { type: Array, default: () => [] },
  statusLabel: { type: String, default: '최근 거래일' }
})

const getTossUrl = (ticker) => {
  if (!ticker) return '#'
  const cleanTicker = String(ticker).replace(/^A/, '').padStart(6, '0')
  return `https://www.tossinvest.com/stocks/A${cleanTicker}/order`
}

// 거래대금 단위 환산 (원 -> 조 / 억)
const formatTradingValue = (val) => {
  if (!val || val === 0) return '0억'

  const ONE_EOK = 100_000_000 // 1억 원
  const ONE_JO = 1_000_000_000_000 // 1조 원

  // 1조 원 이상인 경우 (예: 2조 9,499억 또는 깔끔하게 떨어지면 3조)
  if (val >= ONE_JO) {
    const jo = Math.floor(val / ONE_JO)
    const remEok = Math.round((val % ONE_JO) / ONE_EOK)
    return remEok > 0 ? `${jo}조 ${remEok.toLocaleString()}억` : `${jo}조`
  }

  // 1조 원 미만인 경우 (예: 6,595억)
  const billion = Math.round(val / ONE_EOK)
  return `${billion.toLocaleString()}억`
}

// 시가총액 단위 환산 (네이버 marketValue는 억 원 단위)
const formatMarketCap = (val) => {
  if (!val || val === 0) return '-'
  
  const ONE_EOK = 100_000_000 // 1억 원
  const ONE_JO = 1_000_000_000_000 // 1조 원

  // 1조 이상인 경우
  if (val >= ONE_JO) {
    const jo = Math.floor(val / ONE_JO)
    const remEok = Math.floor((val % ONE_JO) / ONE_EOK)
    return remEok > 0 ? `${jo}조 ${remEok.toLocaleString()}억` : `${jo}조`
  }
  
  // 1억 이상 1조 미만인 경우
  if (val >= ONE_EOK) {
    const eok = Math.floor(val / ONE_EOK)
    return `${eok.toLocaleString()}억`
  }

  return `${val.toLocaleString()}원`
}

// 순매수 금액 (+/- 억 단위)
const formatNet = (value) => {
  if (value === null || value === undefined || value === 0) return '0.0억'
  const valInBillions = value / 100_000_000
  const sign = valInBillions > 0 ? '+' : ''
  return `${sign}${valInBillions.toFixed(1)}억`
}

// 텍스트 색상 클래스
const getAmountClass = (value) => {
  if (!value || value === 0) return 'text-zinc-500 dark:text-zinc-400'
  return value > 0 ? 'text-red-500 dark:text-red-400' : 'text-blue-500 dark:text-blue-400'
}
</script>