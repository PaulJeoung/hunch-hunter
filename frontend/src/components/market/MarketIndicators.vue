<template>
  <section class="space-y-3">
    <!-- 헤더 타이틀 및 날짜 라벨 -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b-2 border-zinc-900 dark:border-zinc-800 pb-2">
      <h3 class="text-sm sm:text-base font-bold text-zinc-900 dark:text-zinc-100 flex items-center gap-1.5">
        <i class="bi bi-bar-chart-line-fill text-emerald-500"></i> 국내 시장 주요 지표
      </h3>
      <span v-if="marketDate" class="self-start sm:self-auto text-xs px-2 py-0.5 border border-zinc-900 dark:border-zinc-700 bg-zinc-200 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 font-mono">
        <i class="bi bi-calendar-event mr-1"></i>{{ statusLabel }} ({{ formatDate(marketDate) }})
      </span>
    </div>

    <!-- 지표 그리드 (모바일 1열, 데스크톱 3열) -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <!-- 1. 급등 TOP 10 -->
      <div class="dot-mini-panel">
        <h4 class="text-xs font-bold text-red-500 dark:text-red-400 mb-2.5 flex items-center justify-between border-b border-zinc-300 dark:border-zinc-800 pb-1.5">
          <span><i class="bi bi-arrow-up-right-circle-fill mr-1"></i>{{ statusLabel }} 급등 TOP 10</span>
          <span class="text-[10px] text-zinc-500 font-mono">KRX</span>
        </h4>
        <div class="space-y-1.5 text-xs">
          <div 
            v-for="(stock, idx) in indicators?.gainers" 
            :key="stock.ticker" 
            class="flex justify-between items-center py-1 border-b border-dashed border-zinc-200 dark:border-zinc-800/80"
          >
            <a 
              :href="getTossUrl(stock.ticker)" 
              target="_blank" 
              rel="noopener noreferrer"
              class="truncate max-w-[150px] font-medium text-zinc-800 dark:text-zinc-200 hover:text-blue-600 dark:hover:text-blue-400 hover:underline inline-flex items-center gap-1 group"
              title="토스증권 시세 조회로 이동"
            >
              <span>{{ idx + 1 }}. {{ stock.name }}</span>
              <i class="bi bi-box-arrow-up-right text-[9px] opacity-0 group-hover:opacity-100"></i>
            </a>
            <span class="text-red-500 dark:text-red-400 font-mono font-bold">
              +{{ stock.change_rate }}%
            </span>
          </div>
          <div v-if="!indicators?.gainers?.length" class="text-center py-4 text-zinc-400 font-mono text-xs">
            [NO DATA]
          </div>
        </div>
      </div>

      <!-- 2. 급락 TOP 10 -->
      <div class="dot-mini-panel">
        <h4 class="text-xs font-bold text-blue-500 dark:text-blue-400 mb-2.5 flex items-center justify-between border-b border-zinc-300 dark:border-zinc-800 pb-1.5">
          <span><i class="bi bi-arrow-down-right-circle-fill mr-1"></i>{{ statusLabel }} 급락 TOP 10</span>
          <span class="text-[10px] text-zinc-500 font-mono">KRX</span>
        </h4>
        <div class="space-y-1.5 text-xs">
          <div 
            v-for="(stock, idx) in indicators?.losers" 
            :key="stock.ticker" 
            class="flex justify-between items-center py-1 border-b border-dashed border-zinc-200 dark:border-zinc-800/80"
          >
            <a 
              :href="getTossUrl(stock.ticker)" 
              target="_blank" 
              rel="noopener noreferrer"
              class="truncate max-w-[150px] font-medium text-zinc-800 dark:text-zinc-200 hover:text-blue-600 dark:hover:text-blue-400 hover:underline inline-flex items-center gap-1 group"
              title="토스증권 시세 조회로 이동"
            >
              <span>{{ idx + 1 }}. {{ stock.name }}</span>
              <i class="bi bi-box-arrow-up-right text-[9px] opacity-0 group-hover:opacity-100"></i>
            </a>
            <span class="text-blue-500 dark:text-blue-400 font-mono font-bold">
              {{ stock.change_rate }}%
            </span>
          </div>
          <div v-if="!indicators?.losers?.length" class="text-center py-4 text-zinc-400 font-mono text-xs">
            [NO DATA]
          </div>
        </div>
      </div>

      <!-- 3. 시가총액 TOP 10 -->
      <div class="dot-mini-panel">
        <h4 class="text-xs font-bold text-amber-500 dark:text-amber-400 mb-2.5 flex items-center justify-between border-b border-zinc-300 dark:border-zinc-800 pb-1.5">
          <span><i class="bi bi-bank2 mr-1"></i>시가총액 TOP 10</span>
          <span class="text-[10px] text-zinc-500 font-mono">KRX</span>
        </h4>
        <div class="space-y-1.5 text-xs">
          <div 
            v-for="(stock, idx) in indicators?.caps" 
            :key="stock.ticker" 
            class="flex justify-between items-center py-1 border-b border-dashed border-zinc-200 dark:border-zinc-800/80"
          >
            <a 
              :href="getTossUrl(stock.ticker)" 
              target="_blank" 
              rel="noopener noreferrer"
              class="truncate max-w-[140px] font-medium text-zinc-800 dark:text-zinc-200 hover:text-blue-600 dark:hover:text-blue-400 hover:underline inline-flex items-center gap-1 group"
              title="토스증권 시세 조회로 이동"
            >
              <span>{{ idx + 1 }}. {{ stock.name }}</span>
              <i class="bi bi-box-arrow-up-right text-[9px] opacity-0 group-hover:opacity-100"></i>
            </a>
            <span class="text-zinc-600 dark:text-zinc-400 font-mono">
              {{ stock.close?.toLocaleString() }}원
            </span>
          </div>
          <div v-if="!indicators?.caps?.length" class="text-center py-4 text-zinc-400 font-mono text-xs">
            [NO DATA]
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  indicators: { type: Object, default: () => null },
  marketDate: { type: String, default: '' },
  statusLabel: { type: String, default: '최근 거래일' }
})

// 토스증권 상세 주문 URL 생성 함수
const getTossUrl = (ticker) => {
  if (!ticker) return '#'
  const cleanTicker = String(ticker).replace(/^A/, '').padStart(6, '0')
  return `https://www.tossinvest.com/stocks/A${cleanTicker}/order`
}

const formatDate = (str) => {
  if (!str || str.length !== 8) return str
  return `${str.substring(0, 4)}-${str.substring(4, 6)}-${str.substring(6, 8)}`
}
</script>