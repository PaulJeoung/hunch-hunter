<template>
  <div class="min-h-screen bg-zinc-100 dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 flex flex-col font-dot selection:bg-emerald-400 selection:text-zinc-950">
    <!-- 헤더: 테마 옆 등급 버튼 이벤트 연결 -->
    <AppHeader 
      :user="user" 
      @login="openLoginModal" 
      @logout="handleLogout" 
      @openTierGuide="isTierGuideOpen = true"
    />

    <!-- 메인 대시보드 -->
    <main class="max-w-7xl mx-auto px-3 sm:px-4 py-4 sm:py-6 flex-1 w-full space-y-6">
      <SignalSectionContainer 
        :user="user"
        v-model:activeTab="activeTab"
        :currentTier="currentTier"
        :isLoading="isLoading"
        :radarData="radarData"
        :betData="betData"
        @openRadarHelp="isHelpModalOpen = true"
        @openBetHelp="isBetHelpModalOpen = true"
        @login="openLoginModal"
      />

      <MarketDashboardContainer 
        :indicators="indicators"
        :volumeTop50="volumeTop50"
        :marketDate="marketDate"
        :statusLabel="statusLabel"
      />

      <!-- 기존 지표 설명 모달들 -->
      <HelpGuideModal :isOpen="isHelpModalOpen" @close="isHelpModalOpen = false" />
      <ClosingBetGuideModal :isOpen="isBetHelpModalOpen" @close="isBetHelpModalOpen = false" />
      <LoginModal 
        :isOpen="isLoginModalOpen" 
        @close="closeLoginModal" 
        @submit="loginWithCredentials"
      />

      <!-- [신규] 회원 등급 설명 모달 -->
      <TierGuideModal :isOpen="isTierGuideOpen" @close="isTierGuideOpen = false" />
    </main>

    <footer class="border-t-2 border-zinc-900 dark:border-zinc-800 py-3 text-center text-xs font-mono text-zinc-500 bg-zinc-50 dark:bg-zinc-950">
      <i class="bi bi-terminal mr-1"></i>HUNCH HUNTER // QUANT HACKER DASHBOARD
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useStockData } from './composables/useStockData'
import AppHeader from './components/layout/AppHeader.vue'
import SignalSectionContainer from './components/containers/SignalSectionContainer.vue'
import MarketDashboardContainer from './components/containers/MarketDashboardContainer.vue'
import HelpGuideModal from './components/radar/HelpGuideModal.vue'
import ClosingBetGuideModal from './components/bet/ClosingBetGuideModal.vue'
import LoginModal from './components/auth/LoginModal.vue'
import TierGuideModal from './components/layout/TierGuideModal.vue'

const {
  user,
  activeTab,
  radarData,
  betData,
  indicators,
  volumeTop50,
  marketDate,
  statusLabel,
  isLoading,
  currentTier,
  isHelpModalOpen,
  isLoginModalOpen,
  openLoginModal,
  closeLoginModal,
  loginWithCredentials,
  handleLogout
} = useStockData()

const isBetHelpModalOpen = ref(false)
const isTierGuideOpen = ref(false) // 등급 설명 모달 상태
</script>