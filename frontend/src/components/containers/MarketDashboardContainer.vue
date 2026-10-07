<template>
  <div class="space-y-6">
    <!-- 1. 급등, 급락, 시총 TOP 10 그리드 -->
    <MarketIndicators 
      :indicators="indicators" 
      :marketDate="marketDate" 
      :statusLabel="statusLabel" 
    />

    <!-- 2. 거래대금 상위 TOP 50 테이블 -->
    <VolumeTopTable 
      :volumeList="volumeTop50" 
      :statusLabel="statusLabel" 
    />
  </div>
</template>

<script setup>
import MarketIndicators from '../market/MarketIndicators.vue'
import VolumeTopTable from '../market/VolumeTopTable.vue'

defineProps({
  indicators: { type: Object, default: () => null },
  volumeTop50: { type: Array, default: () => [] },
  marketDate: { type: String, default: '' },
  statusLabel: { type: String, default: '최근 거래일' }
})
</script>