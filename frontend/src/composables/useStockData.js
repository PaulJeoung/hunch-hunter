import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'
import { supabase } from '../supabase'

// API Base URL 설정 (환경변수 또는 프록시 기본값)
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

export function useStockData() {
  const user = ref(null)
  const activeTab = ref('radar') // 'radar' | 'bet' | 'cross'
  
  // 데이터 상태
  const radarData = ref(null)
  const betData = ref(null)
  const overlapData = ref(null)      // [신규] 5일 중복 포착 데이터
  const indicators = ref(null)
  const volumeTop50 = ref([])

  // 로딩 상태
  const loadingRadar = ref(false)
  const loadingBet = ref(false)
  const loadingOverlap = ref(false)  // [신규] 중복 분석 로딩 상태
  const marketDate = ref('')
  const statusLabel = ref('최근 거래일')
  
  // 가이드 및 로그인 모달 상태
  const isHelpModalOpen = ref(false)
  const isLoginModalOpen = ref(false)

  // 활성 탭에 따른 동적 로딩 & 티어 산출
  const isLoading = computed(() => {
    if (activeTab.value === 'radar') return loadingRadar.value
    if (activeTab.value === 'bet') return loadingBet.value
    if (activeTab.value === 'cross') return loadingOverlap.value
    return false
  })

  const currentTier = computed(() => {
    if (activeTab.value === 'radar') return radarData.value?.tier
    if (activeTab.value === 'bet') return betData.value?.tier
    if (activeTab.value === 'cross') return overlapData.value?.tier
    return ''
  })

  // 1. 공개 시장 데이터 호출 (급등, 급락, 시총 TOP10 및 거래대금 TOP50)
  const fetchPublicData = async () => {
    try {
      const [volRes, indRes] = await Promise.all([
        axios.get(`${API_BASE}/market/volume-top50`),
        axios.get(`${API_BASE}/market/indicators-top10`)
      ])
      volumeTop50.value = volRes.data.data
      indicators.value = indRes.data
      marketDate.value = volRes.data.date
      statusLabel.value = volRes.data.status_label || '최근 거래일'
    } catch (err) {
      console.error('공개 시장 데이터 조회 실패:', err)
    }
  }

  // 2. [탭 1] 세력 매집 흔적 시그널
  const fetchRadarSignals = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    const token = session?.access_token
    if (!token) return

    loadingRadar.value = true
    try {
      const res = await axios.get(`${API_BASE}/radar/signals`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      radarData.value = res.data
    } catch (err) {
      console.error('흔적 레이더 조회 실패:', err)
    } finally {
      loadingRadar.value = false
    }
  }

  // 3. [탭 2] 단기 종가 배팅 시그널
  const fetchBetSignals = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    const token = session?.access_token
    if (!token) return

    loadingBet.value = true
    try {
      const res = await axios.get(`${API_BASE}/closing-bet/signals`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      betData.value = res.data
    } catch (err) {
      console.error('종가 배팅 조회 실패:', err)
    } finally {
      loadingBet.value = false
    }
  }

  // 4. [신규: 탭 3] 최근 5일 중복 포착 및 추천 지속 일수 분석
  const fetchOverlapSignals = async () => {
    const { data: { session } } = await supabase.auth.getSession()
    const token = session?.access_token
    if (!token) return

    loadingOverlap.value = true
    try {
      const res = await axios.get(`${API_BASE}/cross-analysis/overlap-5d`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      overlapData.value = res.data
    } catch (err) {
      console.error('5일 중복 포착 시그널 조회 실패:', err)
    } finally {
      loadingOverlap.value = false
    }
  }

  // 탭 변경 시 미호출 데이터 Lazy Fetching
  watch(activeTab, (newTab) => {
    if (!user.value) return
    if (newTab === 'radar' && !radarData.value) fetchRadarSignals()
    if (newTab === 'bet' && !betData.value) fetchBetSignals()
    if (newTab === 'cross' && !overlapData.value) fetchOverlapSignals()
  })

  // 모달 제어 핸들러
  const openLoginModal = () => {
    isLoginModalOpen.value = true
  }

  const closeLoginModal = () => {
    isLoginModalOpen.value = false
  }

  // 로그인 핸들러
  const loginWithCredentials = async ({ email, password }) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password: password.trim()
      })

      if (error) {
        alert('로그인 실패: ' + error.message)
        return false
      }

      user.value = data.user
      isLoginModalOpen.value = false
      
      // 현재 활성화된 탭에 맞춰 데이터 로드
      if (activeTab.value === 'radar') await fetchRadarSignals()
      else if (activeTab.value === 'bet') await fetchBetSignals()
      else if (activeTab.value === 'cross') await fetchOverlapSignals()
      return true
    } catch (err) {
      console.error('로그인 에러:', err)
      alert('로그인 처리 중 오류가 발생했습니다.')
      return false
    }
  }

  // OAuth 로그인 확장 핸들러
  const loginWithOAuth = async (provider) => {
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: window.location.origin
        }
      })
      if (error) {
        alert(`${provider} 로그인 실패: ` + error.message)
      }
    } catch (err) {
      console.error(`${provider} OAuth 에러:`, err)
    }
  }

  // 로그아웃 핸들러
  const handleLogout = async () => {
    await supabase.auth.signOut()
    user.value = null
    radarData.value = null
    betData.value = null
    overlapData.value = null
  }

  onMounted(async () => {
    fetchPublicData()
    const { data: { session } } = await supabase.auth.getSession()
    if (session) {
      user.value = session.user
      if (activeTab.value === 'radar') fetchRadarSignals()
      else if (activeTab.value === 'bet') fetchBetSignals()
      else if (activeTab.value === 'cross') fetchOverlapSignals()
    }
  })

  return {
    user,
    activeTab,
    radarData,
    betData,
    overlapData,      // 신규 반환
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
    loginWithOAuth,
    handleLogout,
    fetchOverlapSignals
  }
}