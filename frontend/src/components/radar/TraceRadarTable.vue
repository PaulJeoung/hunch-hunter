<template>
  <div>
    <!-- 약 6~7개 행 표시 후 내부 스크롤 (max-h-[300px]) -->
    <div class="overflow-x-auto max-h-[300px] border border-zinc-300 dark:border-zinc-800">
      <table class="w-full text-left text-xs font-mono border-collapse">
        <thead class="sticky top-0 z-10 bg-zinc-200 dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300">
          <tr class="border-b-2 border-zinc-900 dark:border-zinc-700">
            <th class="dot-th min-w-[120px]">종목명</th>
            <th class="dot-th min-w-[90px]">종가</th>
            <th class="dot-th min-w-[80px]">등락률</th>
            <th class="dot-th min-w-[100px]">거래량 이상치(Z)</th>
            <th class="dot-th min-w-[90px]">외인 순매수</th>
            <th class="dot-th min-w-[90px]">기관 순매수</th>
            <th class="dot-th min-w-[70px] text-right">매집 점수</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-zinc-200 dark:divide-zinc-800">
          <tr v-for="item in radarData?.data" :key="item.ticker" class="dot-tr">
            <td class="py-2.5 px-3 font-sans font-bold text-zinc-900 dark:text-zinc-100 truncate">
              {{ item.stocks?.name || item.ticker }}
            </td>
            <td class="py-2.5 px-3 text-zinc-800 dark:text-zinc-200">{{ item.close_price?.toLocaleString() }}원</td>
            <td class="py-2.5 px-3 font-bold" :class="item.day_return >= 0 ? 'text-red-500' : 'text-blue-500'">
              {{ item.day_return > 0 ? '+' : '' }}{{ item.day_return }}%
            </td>
            <td class="py-2.5 px-3 text-emerald-600 dark:text-emerald-400 font-bold">+{{ item.vol_zscore }}σ</td>
            <td class="py-2.5 px-3 text-zinc-600 dark:text-zinc-400">{{ (item.foreign_net / 100000000).toFixed(1) }}억</td>
            <td class="py-2.5 px-3 text-zinc-600 dark:text-zinc-400">{{ (item.institution_net / 100000000).toFixed(1) }}억</td>
            <td class="py-2.5 px-3 text-right font-black text-amber-600 dark:text-amber-400">{{ item.score }}점</td>
          </tr>
          <tr v-if="!radarData?.data || radarData?.data.length === 0">
            <td colspan="7" class="py-8 text-center text-zinc-400 font-mono">
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
</script>