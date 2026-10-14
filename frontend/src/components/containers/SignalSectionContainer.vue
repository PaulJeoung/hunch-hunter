<template>
  <section class="dot-panel">
    <!-- 모바일 / 데스크톱 반응형 탭 헤더 -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 border-b-2 border-zinc-900 dark:border-zinc-800 pb-3">
      <div class="flex items-center gap-2 flex-wrap">
        <!-- 탭 1: 세력 매집 흔적 -->
        <button 
          @click="$emit('update:activeTab', 'radar')"
          class="dot-btn text-xs"
          :class="activeTab === 'radar' 
            ? 'bg-emerald-400 text-zinc-950 dark:bg-emerald-500 font-black' 
            : 'bg-zinc-100 dark:bg-zinc-900 text-zinc-600 dark:text-zinc-400'"
        >
          <i class="bi bi-radar"></i>
          <span>[1] 세력 매집</span>
        </button>

        <!-- 탭 2: 단기 종가 배팅 -->
        <button 
          @click="$emit('update:activeTab', 'bet')"
          class="dot-btn text-xs"
          :class="activeTab === 'bet' 
            ? 'bg-amber-400 text-zinc-950 dark:bg-amber-500 font-black' 
            : 'bg-zinc-100 dark:bg-zinc-900 text-zinc-600 dark:text-zinc-400'"
        >
          <i class="bi bi-lightning-charge-fill"></i>
          <span>[2] 종가 배팅</span>
        </button>

        <!-- [신규] 탭 3: 5일 중복 분석 (지속 일수 카운트) -->
        <button 
          @click="$emit('update:activeTab', 'cross')"
          class="dot-btn text-xs"
          :class="activeTab === 'cross' 
            ? 'bg-indigo-400 text-zinc-950 dark:bg-indigo-500 font-black' 
            : 'bg-zinc-100 dark:bg-zinc-900 text-zinc-600 dark:text-zinc-400'"
        >
          <i class="bi bi-intersect"></i>
          <span>[3] 5일 중복 분석</span>
        </button>

        <!-- 각 탭별 설명 가이드 모달 버튼 -->
        <button 
          v-if="activeTab === 'radar'"
          @click="$emit('openRadarHelp')" 
          class="dot-btn bg-zinc-200 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-300 px-2 text-xs"
          title="세력 매집 지표 가이드"
        >
          <i class="bi bi-question-lg"></i>
        </button>
        <button 
          v-else-if="activeTab === 'bet'"
          @click="$emit('openBetHelp')" 
          class="dot-btn bg-zinc-200 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-300 px-2 text-xs"
          title="단기 종가 배팅 전략 가이드"
        >
          <i class="bi bi-question-lg"></i>
        </button>
      </div>

      <!-- 플랜 뱃지 표시 -->
      <span 
        v-if="currentTier" 
        class="border border-zinc-900 dark:border-emerald-500 px-2 py-0.5 text-xs font-bold self-start sm:self-auto font-mono"
        :class="currentTier === 'PENDING' 
          ? 'bg-amber-100 text-amber-800 border-amber-500' 
          : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-400'"
      >
        <i class="bi bi-shield-shaded mr-1"></i>{{ currentTier }} TIER
      </span>
    </div>

    <!-- 🔒 1. 비로그인 유저 접속 게이트 -->
    <div v-if="!user" class="py-12 text-center border-2 border-dashed border-zinc-400 dark:border-zinc-700 bg-zinc-50 dark:bg-zinc-900/50">
      <i class="bi bi-lock-fill text-3xl text-zinc-400 mb-2 block"></i>
      <p class="text-zinc-700 dark:text-zinc-300 text-sm font-bold mb-1 font-mono">
        PRO 구독 시 열람하실 수 있습니다.
      </p>
      <p class="text-zinc-500 dark:text-zinc-400 text-xs mb-4">
        로그인 후 당일 포착된 정밀 수급 시그널 및 5일 연속 추천 종목을 확인하세요.
      </p>
      <button @click="$emit('login')" class="dot-btn bg-emerald-400 hover:bg-emerald-300 text-zinc-950 text-xs">
        <i class="bi bi-box-arrow-in-right"></i> 로그인 / 시작하기
      </button>
    </div>

    <!-- 로딩 상태 -->
    <div v-else-if="isLoading" class="py-8 text-center text-xs font-mono text-zinc-500">
      <i class="bi bi-arrow-repeat animate-spin inline-block mr-2"></i>ANALYZING_MARKET_DATA...
    </div>

    <!-- 데이터 테이블 및 안내 배너 -->
    <div v-else>
      <TraceRadarTable v-if="activeTab === 'radar'" :radarData="radarData" />
      <ClosingBetTable v-else-if="activeTab === 'bet'" :betData="betData" />
      <OverlapSignalTable v-else-if="activeTab === 'cross'" :overlapData="overlapData" />

      <!-- 🔒 2. 잘림 안내 배너 (PRO DEACTIVE 대기자 및 FREE 안내문 동적 표시) -->
      <div 
        v-if="currentSignalData?.is_truncated" 
        class="mt-3 p-3 text-center text-xs border-2 border-dashed font-bold font-mono"
        :class="currentTier === 'PENDING' 
          ? 'border-amber-400 bg-amber-50 text-amber-900 dark:bg-amber-950/40 dark:text-amber-300' 
          : 'border-zinc-400 bg-zinc-50 text-zinc-600 dark:bg-zinc-900 dark:text-zinc-400'"
      >
        <i class="bi" :class="currentTier === 'PENDING' ? 'bi-hourglass-split mr-1' : 'bi-info-circle mr-1'"></i>
        {{ currentSignalData?.message || 'PRO 구독 시 전체 종목을 열람하실 수 있습니다.' }}
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import TraceRadarTable from '../radar/TraceRadarTable.vue'
import ClosingBetTable from '../bet/ClosingBetTable.vue'
import OverlapSignalTable from '../cross/OverlapSignalTable.vue'

const props = defineProps({
  user: { type: Object, default: null },
  activeTab: { type: String, default: 'radar' },
  currentTier: { type: String, default: '' },
  isLoading: { type: Boolean, default: false },
  radarData: { type: Object, default: null },
  betData: { type: Object, default: null },
  overlapData: { type: Object, default: null } // [신규] 전달받는 5일 중복 포착 데이터
})

defineEmits(['update:activeTab', 'openRadarHelp', 'openBetHelp', 'login'])

// 현재 활성화된 탭의 시그널 데이터 동적 산출 (잘림 여부 배너 체크용)
const currentSignalData = computed(() => {
  if (props.activeTab === 'radar') return props.radarData
  if (props.activeTab === 'bet') return props.betData
  if (props.activeTab === 'cross') return props.overlapData
  return null
})
</script>