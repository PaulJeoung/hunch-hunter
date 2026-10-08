import { supabase } from '../supabase'

export const authService = {
  /**
   * 이메일 회원가입 (신규 신청)
   * requestedRole: 'PRO' 신청 시 DB 트리거에 의해 기본 'DEACTIVE'로 생성됨
   */
  async signUpWithEmail(email, password, requestedRole = 'USER') {
    const { data, error } = await supabase.auth.signUp({
      email: email.trim(),
      password: password.trim(),
      options: {
        data: { role: requestedRole }
      }
    })
    if (error) throw error
    return data
  },

  /**
   * 이메일/비밀번호 로그인
   */
  async signInWithEmail(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email.trim(),
      password: password.trim()
    })
    if (error) throw error
    return data
  },

  /**
   * 소셜(구글, 카카오, 네이버) OAuth 로그인
   * redirect URL을 통해 세션을 획득하고 기존 이메일과 매핑
   */
  async signInWithOAuth(provider) {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: provider.toLowerCase(),
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
        queryParams: {
          access_type: 'offline',
          prompt: 'consent'
        }
      }
    })
    if (error) throw error
    return data
  },

  /**
   * 이미 로그인된 이메일 계정에 추가 소셜 계정 연동 (Identity Linking)
   * 1:1 중복 가입을 방지하고 하나의 유저 프로필로 묶음
   */
  async linkSocialProvider(provider) {
    const { data, error } = await supabase.auth.linkIdentity({
      provider: provider.toLowerCase(),
      options: {
        redirectTo: `${window.location.origin}/auth/callback`
      }
    })
    if (error) throw error
    return data
  },

  /**
   * 소셜 연동 해제
   */
  async unlinkSocialProvider(identity) {
    const { data, error } = await supabase.auth.unlinkIdentity(identity)
    if (error) throw error
    return data
  },

  /**
   * 현재 유저의 연동된 계정 목록 조회 (이메일, 카카오, 네이버 등)
   */
  async getLinkedIdentities() {
    const { data: { user }, error } = await supabase.auth.getUser()
    if (error || !user) return []
    return user.identities || []
  },

  async signOut() {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  }
}