<template>
  <section class="dot-panel">
    <!-- 모바일 / 데스크톱 반응형 탭 헤더 -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 border-b-2 border-zinc-900 dark:border-zinc-800 pb-3">
      <div class="flex items-center gap-2 flex-wrap">
        <!-- 탭 1: 세력 매집 흔적 & 전용 ? 버튼 -->
        <div class="inline-flex items-center gap-1">
          <button 
            @click="$emit('update:activeTab', 'radar')"
            class="dot-btn"
            :class="activeTab === 'radar' 
              ? 'bg-emerald-400 text-zinc-950 dark:bg-emerald-500 font-black' 
              : 'bg-zinc-100 dark:bg-zinc-900 text-zinc-600 dark:text-zinc-400'"
          >
            <i class="bi bi-radar"></i>
            <span>[1] 세력 매집 흔적</span>
          </button>
          <button 
            v-if="activeTab === 'radar'"
            @click="$emit('openRadarHelp')" 
            class="dot-btn bg-zinc-200 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-300 px-2 py-1 text-xs"
            title="세력 매집 흔적 지표 가이드"
          >
            <i class="bi bi-question-lg"></i>
          </button>
        </div>

        <!-- 탭 2: 단기 종가 배팅 & 전용 ? 버튼 -->
        <div class="inline-flex items-center gap-1">
          <button 
            @click="$emit('update:activeTab', 'bet')"
            class="dot-btn"
            :class="activeTab === 'bet' 
              ? 'bg-amber-400 text-zinc-950 dark:bg-amber-500 font-black' 
              : 'bg-zinc-100 dark:bg-zinc-900 text-zinc-600 dark:text-zinc-400'"
          >
            <i class="bi bi-lightning-charge-fill"></i>
            <span>[2] 단기 종가 배팅</span>
          </button>
          <button 
            v-if="activeTab === 'bet'"
            @click="$emit('openBetHelp')" 
            class="dot-btn bg-zinc-200 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-300 px-2 py-1 text-xs"
            title="단기 종가 배팅 매매 가이드"
          >
            <i class="bi bi-question-lg"></i>
          </button>
        </div>
      </div>

      <span 
        v-if="currentTier" 
        class="border border-zinc-900 dark:border-emerald-500 bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400 px-2 py-0.5 text-xs font-bold self-start sm:self-auto font-mono"
      >
        <i class="bi bi-shield-shaded mr-1"></i>{{ currentTier }} TIER
      </span>
    </div>

    <!-- 비로그인 게이트 -->
    <div v-if="!user" class="py-10 text-center border-2 border-dashed border-zinc-400 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-900/50">
      <i class="bi bi-terminal-x text-3xl text-zinc-400 mb-2 block"></i>
      <p class="text-zinc-600 dark:text-zinc-400 text-xs mb-3 font-mono">
        AUTH REQUIRED: {{ activeTab === 'radar' ? 'HUNCH_TRACE' : 'CLOSING_BET' }} ALGORITHM LOCKED
      </p>
      <button @click="$emit('login')" class="dot-btn bg-emerald-400 text-zinc-950 text-xs">
        <i class="bi bi-key-fill"></i> 로그인 후 시그널 열람
      </button>
    </div>

    <!-- 로딩 상태 -->
    <div v-else-if="isLoading" class="py-8 text-center text-xs font-mono text-zinc-500">
      <i class="bi bi-arrow-repeat animate-spin inline-block mr-2"></i>ANALYZING_MARKET_DATA...
    </div>

    <!-- 데이터 테이블 컨테이너 -->
    <div v-else>
      <TraceRadarTable v-if="activeTab === 'radar'" :radarData="radarData" />
      <ClosingBetTable v-else-if="activeTab === 'bet'" :betData="betData" />
    </div>
  </section>
</template>

<script setup>
import TraceRadarTable from '../radar/TraceRadarTable.vue'
import ClosingBetTable from '../bet/ClosingBetTable.vue'

defineProps({
  user: { type: Object, default: null },
  activeTab: { type: String, default: 'radar' },
  currentTier: { type: String, default: '' },
  isLoading: { type: Boolean, default: false },
  radarData: { type: Object, default: null },
  betData: { type: Object, default: null }
})

defineEmits(['update:activeTab', 'openRadarHelp', 'openBetHelp', 'login'])
</script>