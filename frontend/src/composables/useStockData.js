import { ref, computed, watch, onMounted } from 'vue'
import axios from 'axios'
import { supabase } from '../supabase'

// const API_BASE = 'http://localhost:8000/api'
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export function useStockData() {
  const user = ref(null)
  const activeTab = ref('radar') // 'radar' | 'bet'
  
  const radarData = ref(null)
  const betData = ref(null)
  const indicators = ref(null)
  const volumeTop50 = ref([])

  const loadingRadar = ref(false)
  const loadingBet = ref(false)
  const marketDate = ref('')
  const statusLabel = ref('최근 거래일')
  const isHelpModalOpen = ref(false)
  
  // 로그인 모달 상태
  const isLoginModalOpen = ref(false)

  const isLoading = computed(() => activeTab.value === 'radar' ? loadingRadar.value : loadingBet.value)
  const currentTier = computed(() => {
    return activeTab.value === 'radar' ? radarData.value?.tier : betData.value?.tier
  })

  // 1. 공개 시장 데이터 호출
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

  // 2. 세력 매집 흔적 시그널
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

  // 3. 단기 종가 배팅 시그널
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

  // 탭 변경 시 Lazy Fetching
  watch(activeTab, (newTab) => {
    if (!user.value) return
    if (newTab === 'radar' && !radarData.value) fetchRadarSignals()
    if (newTab === 'bet' && !betData.value) fetchBetSignals()
  })

  // 모달 열기 핸들러 (기존 헤더의 간편 로그인 버튼 클릭 시 호출)
  const openLoginModal = () => {
    isLoginModalOpen.value = true
  }

  const closeLoginModal = () => {
    isLoginModalOpen.value = false
  }

  // 실제 ID / PW 기반 로그인 핸들러
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
      await Promise.all([fetchRadarSignals(), fetchBetSignals()])
      return true
    } catch (err) {
      console.error('로그인 에러:', err)
      alert('로그인 중 예외가 발생했습니다.')
      return false
    }
  }

  // 향후 카카오, 네이버, 구글 확장용 OAuth 로그인 핸들러
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

  const handleLogout = async () => {
    await supabase.auth.signOut()
    user.value = null
    radarData.value = null
    betData.value = null
  }

  onMounted(async () => {
    fetchPublicData()
    const { data: { session } } = await supabase.auth.getSession()
    if (session) {
      user.value = session.user
      fetchRadarSignals()
      fetchBetSignals()
    }
  })

  return {
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
    loginWithOAuth,
    handleLogout
  }
}