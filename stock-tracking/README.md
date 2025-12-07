# 📊 Stock Tracking System for n8n

텔레그램 채널에서 주식 종목을 수집하고, 미국/한국 주식을 자동 분석하여 알림을 보내는 n8n 워크플로우 시스템

## 🏗️ 시스템 구조

```
┌─────────────────────────────────────────────────────────────┐
│              Main_Stock_Orchestrator                        │
│         (스케줄/수동 트리거 → 전체 파이프라인 관리)            │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
┌─────────────────────┐ ┌─────────────────────┐
│  🇺🇸 US_Stock_Data   │ │  🇰🇷 KR_Stock_Data   │
│     _Collector      │ │     _Collector      │
│  ────────────────   │ │  ────────────────   │
│  • Alpha Vantage    │ │  • KIS Developers   │
│  • 기술지표         │ │  • DART 공시        │
│  • 펀더멘털         │ │  • 자체 지표 계산    │
│  • 뉴스 감성        │ │                     │
└──────────┬──────────┘ └──────────┬──────────┘
           │                       │
           └───────────┬───────────┘
                       ▼
          ┌─────────────────────────┐
          │  📊 Stock_Analysis      │
          │       _Engine           │
          │  ─────────────────      │
          │  • AI 분석 (GPT-4o)     │
          │  • 매력도 스코어링       │
          │  • 리포트 생성          │
          └───────────┬─────────────┘
                      ▼
          ┌─────────────────────────┐
          │   📱 텔레그램 알림       │
          └─────────────────────────┘
```

## 📁 파일 구조

```
stock-tracking/
├── README.md                      # 이 문서
├── US_Stock_Data_Collector.json   # 미국 주식 데이터 수집
├── KR_Stock_Data_Collector.json   # 한국 주식 데이터 수집
├── Stock_Analysis_Engine.json     # AI 통합 분석
└── Main_Stock_Orchestrator.json   # 메인 오케스트레이터
```

## 🚀 설치 방법

### 1. n8n에 워크플로우 Import

각 JSON 파일을 순서대로 import:

1. `US_Stock_Data_Collector.json`
2. `KR_Stock_Data_Collector.json`
3. `Stock_Analysis_Engine.json`
4. `Main_Stock_Orchestrator.json`

**Import 방법**: n8n → Workflows → Import from File

### 2. API 키 발급

| 서비스 | 용도 | 발급 링크 | 비고 |
|--------|------|----------|------|
| **Alpha Vantage** | 미국 주식 | [alphavantage.co](https://www.alphavantage.co/support/#api-key) | 무료 25 calls/day |
| **KIS Developers** | 한국 주식 | [apiportal.koreainvestment.com](https://apiportal.koreainvestment.com/intro) | 한투 계좌 필요 |
| **DART** | 한국 공시 | [opendart.fss.or.kr](https://opendart.fss.or.kr/) | 무료 10,000 calls/day |
| **OpenAI** | AI 분석 | [platform.openai.com](https://platform.openai.com/) | 유료 |
| **Telegram Bot** | 알림 | [@BotFather](https://t.me/botfather) | 무료 |

### 3. 각 워크플로우 설정

#### US_Stock_Data_Collector
- `Set Ticker` 노드 → `YOUR_ALPHA_VANTAGE_API_KEY` 변경

#### KR_Stock_Data_Collector
- `Set Config` 노드:
  - `YOUR_KIS_APP_KEY` 변경
  - `YOUR_KIS_APP_SECRET` 변경
  - `YOUR_DART_API_KEY` 변경

#### Stock_Analysis_Engine
- `Call US Collector` 노드 → US_Stock_Data_Collector 워크플로우 선택
- `Call KR Collector` 노드 → KR_Stock_Data_Collector 워크플로우 선택
- `OpenAI Model` 노드 → OpenAI Credentials 연결

#### Main_Stock_Orchestrator
- `Telegram Config` 노드 → `YOUR_TELEGRAM_CHAT_ID` 변경
- `Call Analysis Engine` 노드 → Stock_Analysis_Engine 선택
- `Send to Telegram` 노드 → Telegram Bot Credentials 연결
- `OpenAI Extractor` 노드 → OpenAI Credentials 연결

### 4. (선택) TelePilot 설치

비공개 채널 수집을 위해:

1. Settings → Community nodes
2. `@telepilotco/n8n-nodes-telepilot` 설치
3. `Fetch Channel Messages` 노드를 TelePilot으로 교체
4. 텔레그램 계정 인증

## 📊 분석 지표

### 기술적 분석 (40%)
| 지표 | 설명 | 신호 |
|------|------|------|
| RSI | 상대강도지수 (14일) | <30 과매도, >70 과매수 |
| MACD | 이동평균수렴확산 | 히스토그램 양수=상승, 음수=하락 |
| Bollinger Bands | 변동성 밴드 | 하단터치=반등, 상단이탈=과열 |
| 이동평균 | SMA 20/60 | 골든크로스/데드크로스 |

### 펀더멘털 분석 (35%)
| 지표 | 설명 | 기준 |
|------|------|------|
| PER | 주가수익비율 | 업종 평균 대비 저평가 |
| PBR | 주가순자산비율 | <1 자산가치 대비 저평가 |
| ROE | 자기자본이익률 | >15% 우수 |
| 배당수익률 | - | >3% 매력적 |

### 뉴스/감성 분석 (25%)
- 미국: Alpha Vantage 뉴스 감성 점수
- 한국: DART 공시 기반 키워드 분석

## 📱 출력 예시

```
📊 주식 분석 리포트 (2025-12-04)
━━━━━━━━━━━━━━━━━━━━

🇺🇸 NVDA | NVIDIA Corp
📈 매력도: 85/100 🟢

기술적: RSI 58 (중립), MACD 상승 전환
펀더멘털: PER 45.2, ROE 56%

✅ 강력매수
• AI 반도체 수요 지속 증가
• 기술적 조정 후 반등 신호
• HBM 경쟁 우위

⚠️ 리스크: 밸류에이션 부담

━━━━━━━━━━━━━━━━━━━━

🇰🇷 005930 | 삼성전자
📈 매력도: 72/100 🟡

기술적: RSI 42, SMA60 지지
펀더멘털: PER 12.8, PBR 1.1

✅ 매수
• HBM 양산 본격화
• 배당수익률 2.5%
• 반도체 사이클 바닥 근접

⚠️ 리스크: 수출 규제 불확실성

━━━━━━━━━━━━━━━━━━━━
🤖 AI 분석 | 투자 참고용
```

## ⚠️ 주의사항

1. **투자 조언 아님**: AI 분석 결과는 참고용이며, 투자 결정은 본인 책임
2. **API 한도**: 무료 API는 호출 제한 있음 (캐싱 권장)
3. **규제 준수**: 자본시장법에 따라 비영리 개인 용도로만 사용
4. **계정 보안**: TelePilot 사용 시 텔레그램 계정 밴 주의

## 🔧 커스터마이징

### 분석 기준 변경
`Stock_Analysis_Engine.json`의 `AI Analysis` 노드에서 시스템 프롬프트 수정

### 필터링 기준 변경
`Filter Attractive Stocks` 노드에서 매력도 점수 임계값 조정 (기본: 60)

### 스케줄 변경
`Main_Stock_Orchestrator.json`의 `Schedule Trigger` 노드에서 간격 조정 (기본: 2시간)

## 📝 라이선스

개인 사용 목적으로 자유롭게 사용 및 수정 가능

---

**Created with n8n + Claude** 🤖
