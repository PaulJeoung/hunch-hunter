frontend/src/
├── assets/
│   └── styles/
│       └── main.css
├── composables/
│   └── useStockData.js          # API 호출, 인증 토큰 주입, 탭 상태 로직 완전 분리
├── components/
│   ├── layout/
│   │   └── AppHeader.vue        # 네비게이션 헤더
│   ├── containers/              # [신규] 화면 섹션 컨테이너들
│   │   ├── SignalSectionContainer.vue   # 세력 흔적 / 종가 배팅 탭 & 테이블 관리
│   │   └── MarketDashboardContainer.vue # TOP 10 지표 & TOP 50 거래대금 묶음
│   ├── radar/
│   │   ├── TraceRadarTable.vue
│   │   └── HelpGuideModal.vue
│   ├── bet/
│   │   └── ClosingBetTable.vue
│   └── market/
│       ├── MarketIndicators.vue
│       └── VolumeTopTable.vue
├── App.vue                      # 초간결화 (컨테이너 2개 조립만 수행)
└── main.js