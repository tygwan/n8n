# 주식 뉴스 AI 자동화 시스템 설계 문서

**버전**: 1.0
**작성일**: 2025-12-07
**프로젝트**: stock-tracking

---

## 📋 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [시스템 아키텍처](#시스템-아키텍처)
3. [기술 스택 및 비용 분석](#기술-스택-및-비용-분석)
4. [채널 구성 전략](#채널-구성-전략)
5. [데이터베이스 설계](#데이터베이스-설계)
6. [API 엔드포인트 설계](#api-엔드포인트-설계)
7. [n8n Workflow 설계](#n8n-workflow-설계)
8. [메시지 처리 흐름](#메시지-처리-흐름)
9. [구현 단계](#구현-단계)
10. [성능 및 모니터링](#성능-및-모니터링)

---

## 프로젝트 개요

### 목적
텔레그램 채널에서 수집되는 주식 관련 뉴스를 AI로 분석하여 Slack 채널에 자동으로 분류/요약/전송하는 시스템

### 핵심 기능
- ✅ 텔레그램 실시간 메시지 수집 + 과거 데이터 처리
- ✅ AI 기반 테마 분류 및 감성 분석 (GPT-5-mini)
- ✅ 토큰 최적화 (청킹, 배치 처리)
- ✅ Slack 10개 채널 자동 라우팅 (용도별 + 태그 시스템)
- ✅ SQLite 기반 메시지 상태 추적
- ✅ 처리 로그 및 모니터링

### 주요 개선 사항
**현재 시스템**:
- 단순 키워드 매칭
- 단일 Slack 채널 (#stock-alerts)
- AI 분석 없음

**개선 후**:
- GPT-5-mini AI 분석 (테마 분류, 감성 분석, 핵심 사실 추출)
- 10개 Slack 채널 자동 라우팅 (US/KR × 용도별)
- 태그 시스템 (#반도체, #AI, #매수 등)
- 과거 데이터 일괄 처리
- 메시지 처리 상태 추적

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│              Telegram Channels (24/7 수집)               │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│         Telegram Collector (collector.py)                │
│  • 실시간 수집: NewMessage 이벤트 핸들러                 │
│  • 과거 수집: backfill_messages() 함수                   │
│  • SQLite 저장: status='pending'                         │
│  • n8n Webhook: priority ≥4 즉시 전송                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│            SQLite Database (영구 저장)                    │
│  • messages: 메시지 원본 + AI 분석 결과                  │
│  • processing_log: 처리 로그 (단계별 추적)               │
│  • channels: 채널 설정                                   │
│  • themes: 테마 정의                                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│          FastAPI (http://localhost:8000)                 │
│  • GET /messages/pending                                 │
│  • GET /messages/historical?days=7                       │
│  • POST /messages/update-status                          │
│  • GET /processing-status/{message_id}                   │
│  • GET /stats/processing                                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│       n8n Workflow: AI Analysis Engine                   │
│  1. Batch Schedule (매 1시간 / 매일 1AM)                 │
│  2. Fetch Messages                                       │
│  3. Update Status → 'processing'                         │
│  4. GPT-5-mini AI Analysis                              │
│     • 테마 분류 (8개)                                     │
│     • 감성 분석 (매수/매도/중립)                          │
│     • 핵심 사실 추출 (3-5개)                              │
│     • 투자 시사점 생성                                    │
│  5. Channel Router (US/KR × 용도)                        │
│  6. Slack Formatter (태그 + emoji)                       │
│  7. Send to Slack (병렬 전송)                            │
│  8. Save AI Results → DB                                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Slack Workspace (10 channels)               │
│  US: 뉴스, 리포트, 분석, 알람, 조회                      │
│  KR: 뉴스, 리포트, 분석, 알람, 조회                      │
└─────────────────────────────────────────────────────────┘
```

---

## 기술 스택 및 비용 분석

### 기술 스택

| 계층 | 기술 | 역할 |
|------|------|------|
| **수집** | Telethon (Python) | 텔레그램 User API 기반 메시지 수집 |
| **저장** | SQLite + WAL 모드 | 메시지 영구 저장 및 상태 관리 |
| **API** | FastAPI + Uvicorn | RESTful API 서버 |
| **워크플로우** | n8n (Docker) | AI 분석 및 Slack 전송 자동화 |
| **AI 분석** | GPT-5-mini (OpenAI) | 테마 분류, 감성 분석, 요약 생성 |
| **알림** | Slack API | 10개 채널 메시지 전송 |
| **컨테이너** | Docker Compose | n8n 및 서비스 오케스트레이션 |

### GPT-5-mini 비용 분석

**2025년 1월 기준 가격**:
- Input: **$0.150 / 1M tokens**
- Output: **$0.600 / 1M tokens**

**월 예상 사용량**:
```
메시지 수: 100건/day × 30일 = 3,000건/month
평균 입력: 300 tokens/message (원본 텍스트)
평균 출력: 200 tokens/message (분석 결과)
총 토큰: 3,000 × 500 = 1,500,000 tokens/month
최적화 적용 (30% 절감): 1,500,000 × 0.7 = 1,050,000 tokens/month
```

**월 비용 계산**:
```
Input:  700,000 tokens × $0.150 / 1M = $0.105
Output: 350,000 tokens × $0.600 / 1M = $0.210
────────────────────────────────────────────
총 월 비용: $0.315/month (약 460원/월) ✅
```

**비용 절감 전략**:
1. ✅ 고우선순위 메시지만 AI 분석 (priority ≥ 2) → 30% 절감
2. ✅ SQLite UNIQUE 제약으로 중복 제거 → 20% 절감
3. ✅ 배치 처리 (청킹) → 자동 적용

---

## 채널 구성 전략

### 최종 선택: 하이브리드 (용도별 채널 + 태그 시스템)

#### Slack 채널 구성 (10개)

**US 시장 (5개)**:
```
#us-뉴스    → 실시간 뉴스 피드 + 테마 태그
#us-리포트  → 심층 분석 리포트 + 테마 태그
#us-분석    → AI 종목 분석 결과 + 테마 태그
#us-알람    → 긴급 알림 (priority ≥4)
#us-조회    → 과거 데이터 조회/통계
```

**KR 시장 (5개)**:
```
#kr-뉴스    → 실시간 뉴스 피드 + 테마 태그
#kr-리포트  → 심층 분석 리포트 + 테마 태그
#kr-분석    → AI 종목 분석 결과 + 테마 태그
#kr-알람    → 긴급 알림 (priority ≥4)
#kr-조회    → 과거 데이터 조회/통계
```

#### 태그 시스템

**테마 태그** (8개):
```
#반도체  #2차전지  #AI  #바이오  #금융  #코인  #IPO  #배당
```

**감성 태그** (3개):
```
#매수  #매도  #중립
```

**우선순위 Emoji**:
```
🟥 Priority 5 (매우 긴급)
🟧 Priority 4 (긴급)
🟨 Priority 3 (중요)
🟦 Priority 2 (일반)
⬜ Priority 1 (참고)
```

#### 메시지 포맷 예시

```
🟧 [#us-뉴스] 2025-12-07 16:30

#AI #반도체 #매수

📊 NVIDIA, 차세대 Blackwell GPU 공급 부족 지속

• Jensen Huang CEO: "수요가 공급을 압도적으로 초과"
• 주요 고객사: Microsoft, Meta, Amazon 등
• 2025년 상반기까지 공급 부족 예상

💡 투자 시사점: AI 인프라 수요 지속 → 장기 매수 유지

📈 티커: `NVDA`, `AMD`, `MSFT`
🔗 출처: Bloomberg
```

#### 채널 라우팅 로직

| 조건 | 채널 | 비고 |
|------|------|------|
| 티커 포함 + US | #us-뉴스, #us-분석 | 중복 가능 |
| 티커 포함 + KR | #kr-뉴스, #kr-분석 | 중복 가능 |
| Priority ≥ 4 + US | #us-알람 | 긴급 알림 |
| Priority ≥ 4 + KR | #kr-알람 | 긴급 알림 |
| 리포트/분석 키워드 | #us-리포트 or #kr-리포트 | "분석", "전망", "리포트" 포함 시 |
| 과거 데이터 조회 | #us-조회, #kr-조회 | 수동 조회 전용 |

---

## 데이터베이스 설계

### ERD

```
┌─────────────────────────────────────────────────────────┐
│                      messages                            │
├─────────────────────────────────────────────────────────┤
│ id (PK)                INTEGER                           │
│ message_id             INTEGER                           │
│ channel_id             INTEGER                           │
│ channel_name           TEXT                              │
│ text                   TEXT                              │
│ date                   INTEGER (Unix timestamp)          │
│ collected_at           TEXT (ISO 8601)                   │
│                                                           │
│ -- 기본 분석 (collector.py)                              │
│ tickers                TEXT (쉼표 구분)                   │
│ ticker_count           INTEGER                           │
│ sentiment              TEXT                              │
│ priority               INTEGER (1-5)                     │
│ themes                 TEXT (쉼표 구분)                   │
│                                                           │
│ -- AI 분석 결과 (n8n workflow)                           │
│ ai_analyzed            INTEGER (0/1)                     │
│ ai_analyzed_at         TEXT                              │
│ ai_theme_tags          TEXT (JSON 배열)                  │
│ ai_sentiment_tag       TEXT                              │
│ ai_summary             TEXT                              │
│ ai_key_facts           TEXT (JSON 배열)                  │
│ ai_investment_insight  TEXT                              │
│                                                           │
│ -- 처리 상태                                              │
│ status                 TEXT (pending/processing/processed)│
│ processed_at           TEXT                              │
│ slack_channels         TEXT (JSON 배열)                  │
│                                                           │
│ UNIQUE(channel_id, message_id)                           │
└─────────────────────────────────────────────────────────┘
                          │
                          │ 1:N
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  processing_log                          │
├─────────────────────────────────────────────────────────┤
│ id (PK)                INTEGER                           │
│ message_id (FK)        INTEGER → messages.id             │
│ step                   TEXT                              │
│ status                 TEXT (started/success/failed)     │
│ details                TEXT (JSON)                       │
│ error_msg              TEXT                              │
│ started_at             TEXT                              │
│ completed_at           TEXT                              │
└─────────────────────────────────────────────────────────┘
```

### 주요 테이블 스키마

#### messages 테이블

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    channel_name TEXT,
    channel_username TEXT,
    text TEXT,
    date INTEGER,
    collected_at TEXT,
    has_media INTEGER DEFAULT 0,

    -- 기본 분석
    tickers TEXT,
    ticker_count INTEGER DEFAULT 0,
    sentiment TEXT,
    priority INTEGER DEFAULT 1,
    themes TEXT,

    -- AI 분석 결과
    ai_analyzed INTEGER DEFAULT 0,
    ai_analyzed_at TEXT,
    ai_theme_tags TEXT,        -- JSON: ["반도체", "AI"]
    ai_sentiment_tag TEXT,     -- "매수", "매도", "중립"
    ai_summary TEXT,
    ai_key_facts TEXT,         -- JSON: ["사실1", "사실2"]
    ai_investment_insight TEXT,

    -- 처리 상태
    status TEXT DEFAULT 'pending',
    processed_at TEXT,
    sent_to_n8n INTEGER DEFAULT 0,
    sent_to_sheets INTEGER DEFAULT 0,
    slack_channels TEXT,       -- JSON: ["#us-뉴스", "#us-알람"]

    UNIQUE(channel_id, message_id)
);
```

#### processing_log 테이블

```sql
CREATE TABLE processing_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,
    step TEXT NOT NULL,        -- 'fetched', 'ai_analysis', 'slack_sent', 'completed'
    status TEXT NOT NULL,      -- 'started', 'success', 'failed'
    details TEXT,              -- JSON
    error_msg TEXT,
    started_at TEXT,
    completed_at TEXT,

    FOREIGN KEY (message_id) REFERENCES messages(id)
);
```

### 인덱스 전략

```sql
-- WAL 모드 활성화 (동시성 향상)
PRAGMA journal_mode=WAL;

-- 복합 인덱스 (처리 대기 메시지 조회 최적화)
CREATE INDEX idx_messages_status
ON messages(status, priority DESC, date DESC);

-- AI 분석 여부 인덱스
CREATE INDEX idx_messages_ai_analyzed
ON messages(ai_analyzed, status);

-- 테마별 조회 최적화
CREATE INDEX idx_messages_themes
ON messages(themes);

-- 날짜별 조회 최적화
CREATE INDEX idx_messages_date
ON messages(date DESC);

-- 처리 로그 조회 최적화
CREATE INDEX idx_processing_log_msg
ON processing_log(message_id, started_at DESC);
```

---

## API 엔드포인트 설계

### Base URL
```
http://localhost:8000
```

### 엔드포인트 목록

#### 1. GET /messages/pending
**목적**: 미처리 메시지 조회 (실시간 배치용)

**Query Parameters**:
```
limit: int = 100 (1-1000)
min_priority: int = 1 (1-5)
```

**Response**:
```json
{
  "count": 42,
  "messages": [
    {
      "id": 1,
      "message_id": 12345,
      "channel_name": "주식뉴스",
      "text": "...",
      "tickers": "NVDA,AMD",
      "themes": "반도체,AI",
      "priority": 3,
      "status": "pending",
      "collected_at": "2025-12-07T10:00:00"
    }
  ]
}
```

#### 2. GET /messages/historical
**목적**: 과거 미분석 메시지 조회 (일괄 처리용)

**Query Parameters**:
```
days: int = 7 (1-30)
ai_analyzed: bool = false
limit: int = 500 (1-1000)
```

**Response**: `/messages/pending`와 동일

#### 3. POST /messages/update-status
**목적**: 메시지 상태 업데이트 + AI 결과 저장

**Request Body**:
```json
{
  "message_ids": [1, 2, 3],
  "status": "processing",
  "step": "ai_analysis",
  "ai_results": {
    "theme_tags": ["반도체", "AI"],
    "sentiment_tag": "매수",
    "summary": "NVIDIA GPU 공급 부족 지속",
    "key_facts": [
      "Jensen Huang CEO 수요 초과 언급",
      "주요 고객사: Microsoft, Meta, Amazon",
      "2025년 상반기까지 공급 부족 예상"
    ],
    "investment_insight": "AI 인프라 수요 지속 → 장기 매수 유지"
  },
  "slack_channels": ["#us-뉴스", "#us-알람"]
}
```

**Response**:
```json
{
  "updated": 3,
  "message_ids": [1, 2, 3],
  "status": "processing"
}
```

#### 4. GET /processing-status/{message_id}
**목적**: 메시지 처리 상태 조회

**Response**:
```json
{
  "message": { /* 메시지 전체 정보 */ },
  "processing_logs": [
    {
      "step": "ai_analysis",
      "status": "success",
      "started_at": "2025-12-07T10:00:00",
      "completed_at": "2025-12-07T10:00:05"
    }
  ],
  "status_summary": {
    "collected": "2025-12-07T09:00:00",
    "status": "processed",
    "ai_analyzed": true,
    "slack_sent": true,
    "channels": ["#us-뉴스", "#us-알람"]
  }
}
```

#### 5. GET /stats/processing
**목적**: 처리 통계

**Response**:
```json
{
  "by_status": {
    "pending": 42,
    "processing": 5,
    "processed": 2953
  },
  "by_ai_analyzed": {
    "0": 47,
    "1": 2953
  },
  "today_processed": 120,
  "avg_processing_time_minutes": 3.5
}
```

---

## n8n Workflow 설계

### Workflow 구성

#### 1. 실시간 처리 Workflow (매 1시간)

```
[Schedule Trigger: Every 1 hour]
  ↓
[HTTP Request: GET /messages/pending?limit=100]
  ↓
[Split Out: messages 배열]
  ↓
[HTTP Request: POST /messages/update-status (status=processing)]
  ↓
[OpenAI: GPT-5-mini Analysis]
  ↓
[Code: Channel Router]
  ↓
[Code: Slack Formatter]
  ↓
[Slack: Send to Multiple Channels (병렬)]
  ↓
[HTTP Request: POST /messages/update-status (ai_results + status=processed)]
```

#### 2. 과거 데이터 처리 Workflow (매일 1AM)

```
[Schedule Trigger: Daily 1AM]
  ↓
[HTTP Request: GET /messages/historical?days=7&limit=500]
  ↓
[Split Out: messages 배열]
  ↓
[동일한 처리 플로우...]
```

### GPT-5-mini 프롬프트

```yaml
System Message: |
  당신은 주식 뉴스 분석 전문가입니다.

  역할:
  1. 주식 관련 뉴스를 테마별로 분류합니다
  2. 각 뉴스의 핵심 사실을 3-5개 bullet point로 요약합니다
  3. 감성 분석 (매수/매도/중립)을 수행합니다
  4. 투자 시사점을 간결하게 제시합니다

  테마 목록:
  - 반도체: SK하이닉스, 삼성전자, NVIDIA, AMD, HBM, DDR5 등
  - 2차전지: LG에너지, 삼성SDI, 테슬라, 배터리, 리튬 등
  - AI: OpenAI, ChatGPT, MS, 구글, 메타, 애플 등
  - 바이오: 셀트리온, 삼성바이오, 신약, FDA, 임상 등
  - 금융: 금리, 연준, Fed, FOMC, 인플레이션, CPI 등
  - 코인: 비트코인, 이더리움, BTC, ETH, 가상자산 등
  - IPO: IPO, 상장, 공모, 청약 등
  - 배당: 배당, 배당금, 배당률, 고배당 등

  제약사항:
  - 각 뉴스당 최대 200자 요약
  - 객관적 사실 위주, 추측 배제
  - 출처 정보 유지

  출력 형식 (JSON):
  {
    "theme_tags": ["반도체", "AI"],
    "sentiment_tag": "매수",
    "summary": "NVIDIA GPU 공급 부족 지속",
    "key_facts": [
      "Jensen Huang CEO 수요 초과 언급",
      "주요 고객사: Microsoft, Meta, Amazon",
      "2025년 상반기까지 공급 부족 예상"
    ],
    "investment_insight": "AI 인프라 수요 지속 → 장기 매수 유지"
  }

User Message Template: |
  다음 뉴스를 분석해주세요:

  채널: {{ $json.channel_name }}
  티커: {{ $json.tickers }}
  우선순위: {{ $json.priority }}

  내용:
  {{ $json.text }}
```

### Channel Router 로직 (Code 노드)

```javascript
// Channel Router - n8n Code Node
const msg = $input.first().json;
const aiResults = $input.first().json.ai_results;

// 시장 구분
const hasUS = (msg.tickers || '').match(/\b[A-Z]{1,5}\b/);
const hasKR = (msg.tickers || '').match(/\b\d{6}\b/);
const market = hasUS ? 'us' : hasKR ? 'kr' : 'us';

// 용도 결정
let purpose = '뉴스';  // 기본값

// 키워드 기반 용도 분류
const text = msg.text.toLowerCase();
if (text.includes('리포트') || text.includes('분석') || text.includes('전망')) {
  purpose = '리포트';
} else if (msg.ticker_count > 0 && aiResults) {
  purpose = '분석';  // 티커 포함 + AI 분석 완료
}

// 채널 목록
const channels = [];

// 메인 채널
channels.push(`#${market}-${purpose}`);

// 긴급 알람 채널
if (msg.priority >= 4) {
  channels.push(`#${market}-알람`);
}

return [{
  json: {
    ...msg,
    ai_results: aiResults,
    target_channels: channels,
    market: market,
    purpose: purpose
  }
}];
```

### Slack Formatter 로직 (Code 노드)

```javascript
// Slack Formatter - n8n Code Node
const msg = $input.first().json;
const ai = msg.ai_results || {};

// 우선순위 emoji
const priorityEmojis = ['⬜', '🟦', '🟨', '🟧', '🟥'];
const emoji = priorityEmojis[Math.min(msg.priority || 1, 5) - 1];

// 태그 생성
const themeTags = (ai.theme_tags || []).map(t => `#${t}`).join(' ');
const sentimentTag = ai.sentiment_tag ? `#${ai.sentiment_tag}` : '';

// 날짜 포맷
const date = new Date(msg.collected_at).toLocaleString('ko-KR', {
  timeZone: 'Asia/Seoul',
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit'
});

// 메시지 포맷
let slackText = `${emoji} [#${msg.market}-${msg.purpose}] ${date}\n\n`;
slackText += `${themeTags} ${sentimentTag}\n\n`;
slackText += `📊 ${ai.summary || msg.text.substring(0, 100)}\n\n`;

// 핵심 사실
if (ai.key_facts && ai.key_facts.length > 0) {
  ai.key_facts.forEach(fact => {
    slackText += `• ${fact}\n`;
  });
  slackText += '\n';
}

// 투자 시사점
if (ai.investment_insight) {
  slackText += `💡 ${ai.investment_insight}\n\n`;
}

// 티커
if (msg.tickers) {
  slackText += `📈 티커: \`${msg.tickers}\`\n`;
}

// 출처
if (msg.channel_name) {
  slackText += `🔗 출처: ${msg.channel_name}`;
}

return [{
  json: {
    ...msg,
    slackText: slackText
  }
}];
```

---

## 메시지 처리 흐름

### 전체 흐름도

```
1. 텔레그램 수집 (collector.py)
   ↓
2. SQLite 저장 (status=pending)
   ↓
3. n8n Batch Schedule 트리거
   ↓
4. FastAPI /messages/pending 호출
   ↓
5. 메시지 상태 → processing
   ↓
6. GPT-5-mini AI 분석
   ↓
7. Channel Router (시장/용도 결정)
   ↓
8. Slack Formatter (태그 + emoji)
   ↓
9. Slack 전송 (병렬)
   ↓
10. DB 업데이트 (status=processed, ai_results 저장)
    ↓
11. processing_log 기록
```

### 상태 전이도

```
pending → processing → processed
   ↓           ↓            ↓
   ↓        failed ←────────┘
   ↓           ↓
   └─────→ retry (3회까지)
```

### 처리 로그 단계

| Step | 설명 | Success 조건 |
|------|------|-------------|
| `fetched` | API에서 메시지 조회 | 200 OK |
| `ai_analysis` | GPT-5-mini 분석 완료 | JSON 파싱 성공 |
| `slack_sent` | Slack 전송 완료 | 채널 전송 성공 |
| `completed` | DB 업데이트 완료 | status=processed |

---

## 구현 단계

### Phase 1: 데이터베이스 및 API 확장 (1-2일)

**작업 목록**:
1. ✅ SQLite 스키마 확장
   - `messages` 테이블에 AI 분석 필드 추가
   - `processing_log` 테이블 생성
   - 인덱스 최적화

2. ✅ FastAPI 엔드포인트 구현
   - `GET /messages/historical`
   - `POST /messages/update-status`
   - `GET /processing-status/{message_id}`
   - `GET /stats/processing`

3. ✅ 테스트
   - API 엔드포인트 테스트
   - DB 쿼리 성능 테스트

**산출물**:
- `database.py` (수정)
- `api.py` (수정)

### Phase 2: n8n Workflow 구축 (2-3일)

**작업 목록**:
1. ✅ GPT-5-mini 연결 설정
   - OpenAI API 키 설정
   - 프롬프트 최적화

2. ✅ Workflow 노드 구성
   - Schedule Trigger (2개)
   - HTTP Request 노드 (4개)
   - OpenAI 노드
   - Code 노드 (Router, Formatter)
   - Slack 노드 (10개 채널)

3. ✅ 테스트
   - 실시간 처리 테스트 (소량)
   - 과거 데이터 처리 테스트
   - 채널별 메시지 검증

**산출물**:
- n8n Workflow JSON 파일

### Phase 3: Slack 채널 및 통합 테스트 (1일)

**작업 목록**:
1. ✅ Slack 채널 생성
   - 10개 채널 생성 및 Webhook 설정
   - n8n에 채널 ID 등록

2. ✅ E2E 테스트
   - 텔레그램 → SQLite → n8n → Slack 전체 흐름
   - 다양한 시나리오 테스트

3. ✅ 모니터링 설정
   - 처리 통계 대시보드
   - 에러 알림 설정

**산출물**:
- Slack 채널 목록
- 테스트 리포트

### Phase 4: 최적화 및 문서화 (1일)

**작업 목록**:
1. ✅ 성능 최적화
   - 토큰 사용량 모니터링
   - 배치 크기 조정
   - 캐싱 전략 적용

2. ✅ 문서화
   - 운영 매뉴얼 작성
   - 트러블슈팅 가이드

**산출물**:
- 운영 매뉴얼
- 성능 리포트

---

## 성능 및 모니터링

### 주요 성능 지표

| 지표 | 목표값 | 측정 방법 |
|------|--------|----------|
| 처리 속도 | 100개 메시지/5분 | `GET /stats/processing` |
| AI 분석 정확도 | 테마 90%, 감성 85% | 수동 검증 샘플링 |
| 중복 제거율 | 15-20% | SQLite UNIQUE 제약 위반 카운트 |
| 평균 처리 시간 | < 5분 | `collected_at` vs `processed_at` |
| 토큰 사용량 | < 1.05M/month | OpenAI API 대시보드 |
| 월 비용 | < $0.50 | 토큰 사용량 × 단가 |

### 모니터링 대시보드

**주요 메트릭**:
```
1. 메시지 처리 현황
   - 총 수집: 3,000건/월
   - 처리 완료: 2,950건
   - 처리 대기: 50건
   - 실패: 0건

2. AI 분석 통계
   - 분석 완료: 2,950건
   - 평균 처리 시간: 3.5분
   - 토큰 사용량: 980K/월

3. Slack 전송 통계
   - #us-뉴스: 1,200건
   - #kr-뉴스: 1,500건
   - #us-알람: 120건
   - #kr-알람: 100건
   - 기타: 30건

4. 비용 현황
   - 월 토큰 비용: $0.29
   - 예상 연 비용: $3.48
```

### 알림 설정

**에러 알림** (Slack #alerts):
- AI 분석 실패
- Slack 전송 실패
- DB 오류
- API 타임아웃

**일일 리포트** (Slack #kr-조회, #us-조회):
- 처리 통계
- 토큰 사용량
- 주요 뉴스 요약

---

## 부록

### 용어 정의

| 용어 | 설명 |
|------|------|
| **테마** | 주식 관련 8개 분류 (반도체, 2차전지, AI, 바이오, 금융, 코인, IPO, 배당) |
| **감성** | 뉴스 톤 (매수/매도/중립) |
| **우선순위** | 1(참고) ~ 5(매우 긴급) |
| **티커** | 종목코드 (US: NVDA, KR: 005930) |
| **청킹** | 대량 텍스트를 512 토큰 단위로 분할 |
| **배치 처리** | 여러 메시지를 한 번에 처리 |

### 참고 자료

1. [AWS Bedrock Batch Inference](https://aws.amazon.com/blogs/machine-learning/monitor-amazon-bedrock-batch-inference-using-amazon-cloudwatch-metrics/)
2. [Deep learning for text summarization using NLP](https://www.nature.com/articles/s41598-025-20224-1)
3. [Slack AI Innovations 2025](https://slack.com/blog/news/ai-innovations-in-slack)
4. [LangChain Token Limitation Strategies](https://medium.com/@techie_chandan/langchain-token-limitation-handling-strategies-1056db9e11d6)
5. [OpenAI GPT-5-mini Pricing](https://openai.com/pricing)

---

**문서 버전**: 1.0
**최종 수정**: 2025-12-07
**작성자**: AI Assistant
**검토자**: -
