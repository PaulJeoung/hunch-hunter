# HUNCH Hunter
> **국내 주식 퀀트 수급 스크리너 & 종가 배팅 SaaS 플랫폼**

HUNCH Hunter는 KRX의 거래대금 상위 종목을 대상으로 기관·외국인의 비정상적인 매집 흔적을 트레이싱하는 **'그림자 추적 프로그램'**과 당일 장 마감 전 거래대금 및 체결 강도(CVD/OBV) 기반의 **'단기 종가 배팅'** 신호를 자동으로 추출·서빙하는 핀테크 웹 서비스입니다.

---

## 📌 주요 핵심 기능

### 1. 시장 공개 대시보드 (Public)
* **거래대금 TOP 50**: 시장 중심 주도주 실시간/일별 랭킹
* **국내 지표 TOP 10**: 당일(또는 최근 거래일) 급등, 급락, 시가총액 상위 종목 브리핑
* **스마트 마켓 타임 감지**: 장전/장중/장마감/휴일 주기에 맞춰 유효 거래일 및 안내 라벨(`최근 거래일 기준`, `당일 기준` 등) 자동 분기

### 2. 세력 흔적 레이더 (Trace Radar / Protected)
* **유니버스**: 거래대금 상위 500개 종목 추출
* **수급 다이버전스 필터**: 개인 순매도 < 0 AND (외국인 + 기관 순매수) > 0
* **가격 잠잠 & 거래량 이상치**: 최근 5일 변동성(ATR) 축소 구간에서 거래량 Z-Score $\ge 1.2$ 이상인 매집 각인 포착
* **재무 건전성 점검**: OpenDART API 연동을 통한 부채비율 및 흑자 여부 검증
* **RBAC 티어별 열람 제한**:
  * 비로그인: 잠금 화면 및 로그인 유도 모달
  * 일반 회원 (`FREE`): 당일 발굴 상위 3개 종목만 미리보기
  * 구독 회원 (`PRO`): 전체 매집 종목 및 세부 수급 지표 완전 개방

### 3. 🚀 단기 종가 배팅 (Closing Bet / Protected)
* 당일 주도 거래대금 + 체결 강도(CVD 순매수 비율) + 일봉 OBV 강세(Bull/Breakout) 지표 결합
* 1차 목표가(+10%), 2차 목표가(+20%) 및 배팅 점수 자동 산출

---

## 🏗️ 시스템 아키텍처 (System Architecture)

```
┌──────────────────────────────────────────────────────────────────┐
│                   Frontend (Web Application Site)                │
│       Vue 3 (Composition API) + Vite + TailwindCSS + Pinia       │
└─────────────────────────────────▲────────────────────────────────┘
                                  │ HTTPS (REST API)
┌─────────────────────────────────▼────────────────────────────────┐
│                   Backend (Renderer Web Service)                 │
│             FastAPI + Python 3.12 + PyJWT (RBAC Auth)            │
└─────────────────┬───────────────────────────────┬────────────────┘
                  │                               │
┌─────────────────▼───────────────┐ ┌─────────────▼────────────────┐
│   Automated Batch Pipelines     │ │       Database Layer         │
│        (GitHub Actions)         │ │         (Supabase)           │
│  - screener_batch.py            │ │  - PostgreSQL (Signals/Meta) │
│  - closing_bet_batch.py         │ │  - Supabase Auth (JWT)       │
│  - FinanceDataReader / OpenDART │ │  - Row Level Security (RLS)  │
└─────────────────────────────────┘ └──────────────────────────────┘
```

---

## Tech Stack

### Frontend
* **Core**: Vue 3 (Composition API, `<script setup>`), Vite
* **Styling**: TailwindCSS
* **State / Data**: Axios, `@supabase/supabase-js`, Lucide Icons
* **Hosting**: Render.com (Static Site / CDN)

### Backend
* **Framework**: FastAPI, Uvicorn
* **Data Processing**: Pandas, NumPy, FinanceDataReader, pykrx
* **Security & Auth**: PyJWT, Supabase Auth
* **Hosting**: Render.com (Web Service)

### Database & Automation
* **Database**: Supabase (PostgreSQL)
* **External APIs**: OpenDART OpenAPI, Naver Finance
* **CI/CD & Batch**: GitHub Actions (`cron: '0 7 * * 1-5'`)

---

## Project Architecture

```text
shadow-raiders/
├── .github/
│   └── workflows/
│       └── daily_batch.yml       # 장 마감 후 자동 수집 GitHub Actions 워크플로우
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── security.py       # JWT 토큰 디코딩 및 RBAC 인가
│   │   ├── routers/
│   │   │   ├── market.py         # 공개 시장 지표 (거래대금 TOP 50, 급등락 TOP 10)
│   │   │   ├── radar.py          # 매집 시그널 API (보호)
│   │   │   └── closing_bet.py    # 종가 배팅 시그널 API (보호)
│   │   └── main.py               # FastAPI 진입점 및 CORS 설정
│   ├── screener_batch.py         # 일일 수집/점수화 배치
│   ├── closing_bet_batch.py      # 종가 배팅 일일 수집 배치
│   ├── requirements.txt          # 백엔드 의존성 파일
│   └── .env                      # 백엔드 환경 변수 (Git 추적 제외)
├── frontend/
│   ├── public/
│   │   └── _redirects            # SPA 라우팅 새로고침(404) 방지
│   ├── src/
│   │   ├── assets/styles/
│   │   │   └── main.css          # Tailwind 커스텀 유틸리티 클래스
│   │   ├── components/
│   │   │   ├── containers/       # 섹션별 뷰 컨테이너 (Dashboard / Signals)
│   │   │   ├── layout/           # AppHeader 등
│   │   │   ├── market/           # 공개 시장 지표 컴포넌트
│   │   │   └── radar/            # 테이블 및 가이드 모달
│   │   ├── composables/
│   │   │   └── useStockData.js   # API 호출 & 상태 관리 컴포저블
│   │   ├── supabase.js           # Supabase 클라이언트 초기화
│   │   ├── App.vue               # 최상위 프레임워크 뷰
│   │   └── main.js
│   ├── package.json
│   ├── vite.config.js
│   └── .env.development         # 프론트엔드 환경 변수
└── .gitignore
```

---

## Environment Variables

### 1. Backend (`backend/.env`)
```env
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="eyJhbGciOi... (service_role 키 또는 anon 키)"
SUPABASE_JWT_SECRET="your-supabase-jwt-secret"
OPENDART_API_KEY="your-opendart-api-key"
```

### 2. Frontend (`frontend/.env.development`, `frontend/.env.production`)
```env
VITE_API_BASE_URL="http://localhost:8000/api" # (배포 시: https://stock-tracker-api.netilify.com/api)
VITE_SUPABASE_URL="https://your-project.supabase.co"
VITE_SUPABASE_ANON_KEY="eyJhbGciOi... (anon public 키)"
```

### 3. GitHub Secrets (저장소 Settings ➔ Secrets and variables ➔ Actions)
* `SUPABASE_URL`
* `SUPABASE_KEY` (service_role Secret Key 권장)
* `OPENDART_API_KEY`

---

## Getting Started For Local

### 1. Database 설정 (Supabase SQL Editor)
프로젝트 초기화 시 다음 테이블을 생성합니다:
* `stocks` (종목 마스터)
* `accumulation_signals` (세력 매집 흔적)
* `stock_reports` (DART 재무 분석 리포트)
* `closing_bet_signals` (종가 배팅 신호)
* `user_profiles` (회원 티어 및 RBAC 권한)

### 2. 백엔드 실행 (FastAPI)
```powershell
cd backend

# 가상환경 생성 및 활성화
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 라이브러리 설치
pip install -r requirements.txt

# 데이터 1회 수동 배치 수집 (필요 시)
python screener_batch.py
python closing_bet_batch.py

# 백엔드 서버 가동
python -m uvicorn app.main:app --reload --port 8000
```
* Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. 프론트엔드 실행 (Vue 3 + Vite)
```powershell
cd frontend

# 패키지 설치
npm install

# 로컬 개발 서버 실행
npm run dev
```
* 기본 접속 주소: [http://localhost:5173](http://localhost:5173)

---

## Production & CI/CD

1. **배치 자동화 (GitHub Actions)**:
   * 매주 월~금 16:00 KST (07:00 UTC)에 `daily_batch.yml`이 자동 구동되어 최신 수급/시세를 파싱하고 Supabase에 Upsert합니다.
2. **백엔드 (Render Web Service)**:
   * GitHub `main` 브랜치 변경 사항 감지 후 자동 배포 (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
3. **프론트엔드 (Render Static Site)**:
   * Vite 기반 빌드 산출물(`dist`)을 CDN으로 무중단 서빙
