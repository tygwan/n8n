# Stock News Automation System

텔레그램 채널에서 주식 뉴스를 수집하고, AI로 분석하여 테마별 Slack 채널로 자동 라우팅하는 시스템

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Stock News Automation                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    │                               │                               │
    ▼                               ▼                               ▼
┌─────────┐                   ┌─────────┐                     ┌─────────┐
│Telegram │ ──Telethon API──▶ │ SQLite  │ ──FastAPI REST──▶  │  n8n    │
│Channels │                   │   DB    │                     │Workflow │
└─────────┘                   └─────────┘                     └────┬────┘
                                                                   │
                                                          GPT-4o-mini
                                                                   │
                              ┌────────────────────────────────────┼────┐
                              │                                    │    │
                              ▼                                    ▼    ▼
                        ┌──────────┐                         ┌──────────┐
                        │  Slack   │ ◀── Theme Routing ────  │  Slack   │
                        │ Channels │                         │ Channels │
                        └──────────┘                         └──────────┘

Slack Channels (10개):
├── stock-반도체  (#반도체)
├── stock-ai      (#AI)
├── stock-바이오  (#바이오)
├── stock-금융    (#금융, #코인)
├── stock-ipo     (#IPO, #배당)
├── stock-시황    (#시황, 시황 타입)
├── stock-alerts  (priority >= 4)
├── stock-daily   (기본 채널)
├── stock-매수    (#매수, #bullish)
└── stock-매도    (#매도, #bearish)
```

## 개발 여정 (Development Journey)

### Phase 1: 초기 설계와 시행착오

처음에는 단순한 구조로 시작했습니다:
- 텔레그램 메시지 수집 → 스프레드시트 저장

**문제점**:
- 스프레드시트는 대량 데이터 처리에 부적합
- 실시간 분석이 어려움
- 테마별 분류가 수동으로 필요

### Phase 2: 아키텍처 재설계

SQLite + FastAPI 조합으로 전환:
```
telegram_collector/
├── collector.py   # Telethon 기반 수집기
├── database.py    # SQLite 스키마 및 쿼리
└── api.py         # FastAPI REST 엔드포인트
```

**개선점**:
- WAL 모드로 동시 읽기/쓰기 지원
- REST API로 n8n 연동 용이
- 인덱싱으로 빠른 쿼리

### Phase 3: n8n 워크플로우 통합

초기에는 여러 개의 워크플로우를 만들었습니다:
- `Stock News AI Analyzer` - 실시간 분석용
- `Historical Data Backfill Processor` - 과거 데이터 처리용
- `Telegram Batch Processor` - 초기 버전
- `Telegram Channel Collector` - 초기 버전

**문제점**:
- 워크플로우가 분산되어 관리 어려움
- 중복 로직 발생
- Slack 라우팅이 명확하지 않음

### Phase 4: 통합 워크플로우 완성

**Stock News Processor (Unified)** - 최종 버전

모든 기능을 하나의 워크플로우로 통합:

```
┌─────────────────────────────────────────────────────────────────┐
│           Stock News Processor (Unified)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐                           │
│  │   Hourly     │    │   Manual     │                           │
│  │  Schedule    │    │  Trigger     │                           │
│  └──────┬───────┘    └──────┬───────┘                           │
│         │                   │                                    │
│         └─────────┬─────────┘                                    │
│                   ▼                                              │
│         ┌─────────────────┐                                      │
│         │ Fetch Messages  │ (limit: 10,000)                      │
│         │  (unanalyzed)   │                                      │
│         └────────┬────────┘                                      │
│                  ▼                                               │
│         ┌─────────────────┐                                      │
│         │ Check Messages  │                                      │
│         │     Exist       │───No───▶ Stop                        │
│         └────────┬────────┘                                      │
│                  │ Yes                                           │
│                  ▼                                               │
│         ┌─────────────────┐                                      │
│         │ Batch Messages  │ (10 per batch)                       │
│         │   for GPT       │                                      │
│         └────────┬────────┘                                      │
│                  ▼                                               │
│         ┌─────────────────┐                                      │
│         │  GPT-4o-mini    │                                      │
│         │   Analysis      │                                      │
│         └────────┬────────┘                                      │
│                  ▼                                               │
│         ┌─────────────────┐                                      │
│         │ Parse Response  │ + Channel Routing                    │
│         └────────┬────────┘                                      │
│                  ▼                                               │
│         ┌─────────────────┐                                      │
│         │  Update DB      │                                      │
│         └────────┬────────┘                                      │
│                  ▼                                               │
│         ┌─────────────────┐                                      │
│         │ Route to Slack  │ (theme-based)                        │
│         │   Channels      │                                      │
│         └────────┬────────┘                                      │
│                  ▼                                               │
│         ┌─────────────────┐                                      │
│         │ Send to Slack   │                                      │
│         └────────┬────────┘                                      │
│                  ▼                                               │
│         ┌─────────────────┐                                      │
│         │  Mark Sent      │                                      │
│         └────────┬────────┘                                      │
│                  ▼                                               │
│         ┌─────────────────┐                                      │
│         │ Log Completion  │                                      │
│         └─────────────────┘                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 해결한 주요 문제들

### 1. Docker 환경에서 localhost 접근 불가

**문제**: n8n이 Docker 컨테이너에서 실행될 때 `localhost:8000`으로 FastAPI 접근 불가

**해결**: 모든 API URL을 `http://host.docker.internal:8000`으로 변경

### 2. Mark Sent to Slack JSON 파싱 오류

**문제**: `JSON parameter needs to be valid JSON [item 0]`

**원인**: `$json.message_ids`가 Slack 응답을 참조하고 있었음

**해결**:
```javascript
// Before (오류)
{{ $json.message_ids }}

// After (정상)
={{ JSON.stringify({ "message_ids": $('Route to Slack Channels').item.json.message_ids }) }}
```

### 3. 메시지 수집 기준 변경

**문제**: 개수 기반(200개) 수집은 기간 파악이 어려움

**해결**: 기간 기반 수집으로 변경 (기본 14일)
```python
# collector.py
min_date = datetime.now() - timedelta(days=days)
if message.date.replace(tzinfo=None) < min_date:
    break
```

### 4. Slack 채널 라우팅

**문제**: 테마별 분류가 명확하지 않음

**해결**: 태그 기반 매핑 시스템 구현
```javascript
const CHANNEL_MAP = {
  '#반도체': 'stock-반도체',
  '#AI': 'stock-ai',
  '#바이오': 'stock-바이오',
  '#금융': 'stock-금융',
  '#코인': 'stock-금융',
  '#IPO': 'stock-ipo',
  '#배당': 'stock-ipo',
  '#시황': 'stock-시황',
  '#매수': 'stock-매수',
  '#매도': 'stock-매도'
};
```

## 파일 구조

```
stock-tracking/
├── README.md                    # 이 문서
├── telegram_collector/
│   ├── collector.py             # Telethon 기반 메시지 수집기
│   ├── database.py              # SQLite 스키마 및 쿼리 함수
│   ├── api.py                   # FastAPI REST 엔드포인트
│   └── telegram_data.db         # SQLite 데이터베이스
└── workflow/
    └── Stock_News_Processor_Unified.json  # 통합 n8n 워크플로우
```

## 설치 및 실행

### 1. 의존성 설치

```bash
cd telegram_collector
pip install telethon fastapi uvicorn
```

### 2. Telegram API 설정

[my.telegram.org](https://my.telegram.org)에서 API ID/Hash 발급

### 3. 메시지 수집 시작

```bash
python collector.py
```

- 처음 실행 시 Telegram 인증 필요
- 채널 선택 및 기간 설정 (기본 14일)

### 4. API 서버 실행

```bash
python api.py
# 또는
uvicorn api:app --host 0.0.0.0 --port 8000
```

### 5. n8n 워크플로우 Import

1. n8n → Workflows → Import from File
2. `workflow/Stock_News_Processor_Unified.json` 선택
3. Credentials 연결:
   - OpenAI API (GPT-4o-mini)
   - Slack Bot Token

### 6. Slack 채널 생성

다음 채널들을 Slack에서 생성:
- `stock-반도체`, `stock-ai`, `stock-바이오`
- `stock-금융`, `stock-ipo`, `stock-시황`
- `stock-alerts`, `stock-daily`
- `stock-매수`, `stock-매도`

## GPT 분석 포맷

각 메시지는 다음 형식으로 분석됩니다:

```json
{
  "id": 12345,
  "theme_tags": "#반도체,#AI",
  "sentiment_tag": "#bullish",
  "summary": "엔비디아 실적 발표 예정, 시장 기대감 상승",
  "key_facts": "Q4 실적 발표 1/24, 예상 EPS $4.50",
  "investment_insight": "단기 변동성 예상, 실적 확인 후 진입 권장",
  "message_type": "뉴스",
  "priority": 4
}
```

### 테마 태그
- 섹터: `#반도체`, `#AI`, `#바이오`, `#금융`, `#코인`, `#IPO`, `#배당`
- 시그널: `#매수`, `#매도`, `#관망`
- 이벤트: `#실적`, `#공시`, `#이슈`, `#시황`

### 메시지 타입
- `시황`: 시장 개요, 지수 동향
- `뉴스`: 속보, 기업 발표
- `리포트`: 애널리스트 리포트
- `분석`: 기술적/펀더멘털 분석
- `알림`: 가격 알림, 급등락

### 우선순위 (1-5)
- 5: 긴급 (급등/급락, 속보)
- 4: 높음 (주요 가격 변동)
- 3: 중간 (일반 뉴스)
- 2: 낮음 (시장 정보)
- 1: 최소 (노이즈)

## API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/messages/unanalyzed` | AI 미분석 메시지 조회 |
| PUT | `/messages/{id}/ai-analysis` | AI 분석 결과 저장 |
| POST | `/messages/sent-to-slack` | Slack 전송 완료 표시 |
| GET | `/stats/processing` | 처리 현황 통계 |
| GET | `/messages/historical` | 과거 데이터 조회 |

## 운영 가이드

### 실시간 처리
- 워크플로우가 매시간 자동 실행
- 미분석 메시지가 없으면 자동 중단

### 과거 데이터 백필
1. `Manual Trigger (Backfill)` 버튼 클릭
2. 최대 10,000개 메시지 일괄 처리
3. 배치당 10개씩 GPT 분석

### 데이터 초기화
```bash
# telegram_data.db 삭제 후 collector.py 재실행
rm telegram_collector/telegram_data.db
python collector.py
```

## 주의사항

- **API 비용**: GPT-4o-mini 사용량에 따른 OpenAI 비용 발생
- **Rate Limit**: Telegram API 및 Slack API 제한 고려
- **투자 조언 아님**: AI 분석 결과는 참고용이며 투자 결정은 본인 책임

---

**Built with**: Python, Telethon, FastAPI, SQLite, n8n, GPT-4o-mini, Slack
