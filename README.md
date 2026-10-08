# HUNCH Hunter
> **국내 주식 퀀트 수급 스크리너 & 종가 배팅 SaaS 플랫폼**

HUNCH Hunter는 KRX 전 종목 중 거래대금 상위 종목을 대상으로 기관·외국인의 비정상적인 매집 흔적을 추적하는 **'그림자 추적(Trace Radar)'**과 당일 장 마감 전 거래대금 및 체결 강도(CVD/OBV) 기반의 **'단기 종가 배팅(Closing Bet)'** 신호를 자동 추출·서빙하는 핀테크 웹 서비스입니다.

---

## Function

### 1. 시장 공개 대시보드
* **거래대금 TOP 50**: 시장 중심 주도주 실시간/일별 랭킹 제공
* **국내 지표 TOP 10**: 당일(또는 최근 거래일) 급등, 급락, 시가총액 상위 종목 브리핑
* **스마트 마켓 타임 감지**: 장전/장중/장마감/휴일 주기에 맞춰 유효 거래일 및 안내 라벨(`최근 거래일 기준`, `당일 기준` 등) 자동 분기

### 2. Trace Radar
* **유니버스**: 거래대금 상위 500개 종목 스크리닝
* **수급 다이버전스 필터**: 개인 순매도 < 0 AND (외국인 + 기관 순매수) > 0
* **가격 잠잠 & 거래량 이상치**: 최근 5일 변동성(ATR) 축소 구간에서 거래량 Z-Score $\ge 1.2$ 포착
* **재무 건전성 점검**: OpenDART API 연동을 통한 부채비율 및 흑자 여부 검증
* **RBAC 티어별 열람 제한**:
  * 비로그인: 잠금 화면 및 로그인 유도 모달
  * 일반 회원 (`FREE`): 당일 발굴 상위 3개 종목 미리보기
  * 승인 대기 회원 (`PRO / DEACTIVE`): 상위 2개 종목 열람 및 승인 대기 안내 메시지
  * 정식 구독 회원 (`PRO / ACTIVE`, `ADMIN`): 전체 매집 종목 및 세부 수급 지표 완전 개방

### 3. 단기 종가 배팅 Closing Bet
* 당일 주도 거래대금 + 체결 강도(CVD 순매수 비율) + 일봉 OBV 강세(Bull/Breakout) 지표 결합
* 1차 목표가(+10%), 2차 목표가(+20%) 및 배팅 점수 자동 산출

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                   Frontend (Web Application Site)                │
│   Vue 3 (Composition API) + Vite + TailwindCSS (Retro Dot Theme) │
│     - Reverse Proxy: /api/* -> Backend (도메인/경로 은닉)          │
└─────────────────────────────────▲────────────────────────────────┘
                                  │ HTTPS (REST API Proxy)
┌─────────────────────────────────▼────────────────────────────────┐
│                   Backend (Render Web Service)                   │
│       FastAPI + Python 3.12 + PyJWT (RBAC) + /health Ping        │
└─────────────────┬───────────────────────────────┬────────────────┘
                  │                               │
┌─────────────────▼───────────────┐ ┌─────────────▼────────────────┐
│   Automated Batch Pipelines     │ │       Database Layer         │
│        (GitHub Actions)         │ │         (Supabase)           │
│  - screener_batch.py (매일 16:00)│ │  - PostgreSQL (Signals/Meta) │
│  - closing_bet_batch.py         │ │  - user_profiles (티어/상태)  │
│  - keep_alive.yml (10분 간격 Ping)│ │  - Row Level Security (RLS) │
└─────────────────────────────────┘ └──────────────────────────────┘
```

---

## Project Architecture

```text
shadow-raiders/
├── .github/
│   └── workflows/
│       ├── daily_batch.yml       # 장 마감 후 자동 수집 GitHub Actions
│       └── keep_alive.yml      
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py         # 라우터 prefix/태그 상수 관리
│   │   │   └── security.py       # JWT 검증 및 회원 권한/구독상태(subscription_status) 인가
│   │   ├── routers/
│   │   │   ├── __init__.py       # api_router 통합 라우터
│   │   │   ├── market.py       
│   │   │   ├── radar.py         
│   │   │   └── closing_bet.py   
│   │   └── main.py               # FastAPI 진입점, CORS 설정, 환경별 /docs 비활성화, /health
│   ├── screener_batch.py         
│   ├── closing_bet_batch.py      
│   ├── requirements.txt          # 백엔드 의존성 파일
│   └── .env                    
├── frontend/
│   ├── public/
│   │   └── _redirects           
│   ├── src/
│   │   ├── assets/styles/
│   │   │   └── main.css          # 레트로 도트 컴포넌트/유틸리티 클래스
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   └── LoginModal.vue             # 시큐어 코딩 적용 로그인 모달
│   │   │   ├── containers/
│   │   │   │   ├── SignalSectionContainer.vue 
│   │   │   │   └── MarketDashboardContainer.vue 
│   │   │   ├── layout/
│   │   │   │   ├── AppHeader.vue              # 상단 헤더, 도트 로고, 테마 스위치
│   │   │   │   └── TierGuideModal.vue      
│   │   │   ├── market/
│   │   │   │   ├── MarketIndicators.vue       
│   │   │   │   └── VolumeTopTable.vue       
│   │   │   ├── radar/
│   │   │   │   ├── TraceRadarTable.vue       
│   │   │   │   └── HelpGuideModal.vue        
│   │   │   └── bet/
│   │   │       ├── ClosingBetTable.vue       
│   │   │       └── ClosingBetGuideModal.vue   
│   │   ├── composables/
│   │   │   ├── useStockData.js   # API 통신, 세션 상태 및 탭 제어 Composable
│   │   │   └── useTheme.js       # 다크/라이트 모드 관리 Composable
│   │   ├── supabase.js          
│   │   ├── App.vue               
│   │   └── main.js
│   ├── index.html               
│   ├── package.json
│   ├── vite.config.js         
│   ├── .env.development       
│   └── .env.production        
└── .gitignore