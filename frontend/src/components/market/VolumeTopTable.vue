<template>
  <section class="dot-panel space-y-3">
    <div class="flex items-center justify-between border-b-2 border-zinc-900 dark:border-zinc-800 pb-3">
      <h3 class="text-sm sm:text-base font-bold text-zinc-900 dark:text-zinc-100 flex items-center gap-1.5">
        <i class="bi bi-cash-stack text-emerald-500"></i> {{ statusLabel }} 거래대금 TOP 50
      </h3>
      <span class="text-[10px] sm:text-xs text-zinc-500 font-mono">통합 코스피/코스닥</span>
    </div>

    <!-- 모바일 터치 대응 가로 스크롤 및 고정 높이 -->
    <div class="overflow-x-auto max-h-[460px] border border-zinc-300 dark:border-zinc-800">
      <table class="w-full text-left text-xs font-mono">
        <thead class="sticky top-0 bg-zinc-200 dark:bg-zinc-900 text-zinc-700 dark:text-zinc-300 z-10">
          <tr>
            <th class="dot-th w-12 text-center">순위</th>
            <th class="dot-th min-w-[120px]">종목명</th>
            <th class="dot-th min-w-[90px]">현재가</th>
            <th class="dot-th min-w-[80px]">등락률</th>
            <th class="dot-th min-w-[100px] text-right">거래대금</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-zinc-200 dark:divide-zinc-800">
          <tr v-for="(item, idx) in volumeList" :key="item.ticker" class="dot-tr">
            <td class="py-2 px-2 text-center text-zinc-500 font-bold">{{ idx + 1 }}</td>
            <td class="py-2 px-2 sm:px-3 font-sans font-bold text-zinc-900 dark:text-zinc-100 truncate">
              {{ item.name }}
            </td>
            <td class="py-2 px-2 sm:px-3 text-zinc-800 dark:text-zinc-200">
              {{ item.close?.toLocaleString() }}원
            </td>
            <td class="py-2 px-2 sm:px-3 font-bold" :class="item.change_rate >= 0 ? 'text-red-500' : 'text-blue-500'">
              {{ item.change_rate > 0 ? '+' : '' }}{{ item.change_rate }}%
            </td>
            <td class="py-2 px-2 sm:px-3 text-right text-zinc-700 dark:text-zinc-300 font-bold">
              {{ (item.trading_value / 100000000).toLocaleString(undefined, { maximumFractionDigits: 0 }) }}억
            </td>
          </tr>
          <tr v-if="!volumeList || volumeList.length === 0">
            <td colspan="5" class="py-8 text-center text-zinc-400 font-mono">
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
</script>