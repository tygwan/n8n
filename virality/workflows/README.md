# Project Piehands - n8n Workflow Implementation

## 📋 Overview

Project Piehands를 위한 4개의 핵심 AI 에이전트 워크플로우입니다.

| Agent | 파일명 | 목적 | 트리거 |
|-------|--------|------|--------|
| 1 | `agent1_market_insight.json` | Blue Ocean 기회 발굴 | Daily 9AM |
| 2 | `agent2_monetization_fds.json` | 정산 & 어뷰징 탐지 | Daily 6AM |
| 3 | `agent3_growth_experiment.json` | A/B 테스트 | Webhook + Daily 9AM |
| 4 | `agent4_business_intelligence.json` | Weekly Business Review | Monday 8AM |

---

## 🚀 Quick Start

### Step 1: n8n 접속
```
http://localhost:5678
```

### Step 2: Workflow Import
1. n8n 대시보드에서 **"Add workflow"** 클릭
2. 우측 상단 **"..."** 메뉴 → **"Import from File"**
3. 각 JSON 파일을 선택하여 import

### Step 3: Credentials 설정
각 워크플로우에 필요한 credentials를 설정합니다:

| Service | 필요한 워크플로우 | 설정 방법 |
|---------|------------------|----------|
| OpenAI API | 모든 Agent | Settings → Credentials → Add → OpenAI |
| Slack | Agent 1, 2, 3, 4 | Settings → Credentials → Add → Slack |
| Gmail | Agent 4 | Settings → Credentials → Add → Gmail |

---

## 📦 Workflow Details

### Agent 1: Market Insight (Blue Ocean Finder)
**목적**: 경쟁사가 놓친 TikTok 트렌드 기회를 발굴하고 미션 전략 수립

**노드 구성**:
```
Schedule Trigger (9AM)
    ├→ Get TikTok Trends (HTTP)
    └→ Get Competitor Data (HTTP)
           ↓
    Merge & Analyze (Code)
           ↓
    AI Strategic Analysis (GPT-4)
           ↓
    Parse Response (Code)
           ↓
    Slack Alert (#market-insights)
```

**주요 기능**:
- TikTok 트렌드와 경쟁사 미션 교차 분석
- Blue Ocean 키워드 자동 발굴
- 미션 설계 및 성공 방정식 제안
- Slack 자동 알림

**커스터마이징**:
- `Get TikTok Trends` 노드의 URL을 실제 TikTok API로 교체
- `Get Competitor Data` 노드를 내부 DB/API로 연결

---

### Agent 2: Monetization & Risk (FDS)
**목적**: 공정한 보상 정산 및 어뷰징 원천 차단

**노드 구성**:
```
Schedule Trigger (6AM)
    ↓
Get Creator View Data (HTTP)
    ↓
Prepare Settlement Data (Code)
    ↓
Calculate Dynamic Reward (Code)
    ↓
AI Fraud Detection (GPT-4)
    ↓
Process FDS Result (Code)
    ↓
Check Risk Level (If)
    ├→ [High Risk] Alert: High Risk (Slack #risk-alerts)
    └→ [Low Risk] Log: Approved Settlement (Slack #settlements)
```

**Dynamic Pricing Logic**:
```javascript
// Base rate: $0.5 per 1K views
// Grade multipliers: S(1.5x), A(1.2x), B(1.0x), C(0.8x)
// Category bonuses: Tech(1.15x), Beauty(1.2x), etc.
// Season multiplier: Peak(1.3x)
// Max cap: $500 per mission
```

**FDS 탐지 기준**:
- 새벽 시간대 급격한 조회수 상승 (봇 의심)
- 낮은 engagement rate (< 1%)
- 평균 시청 시간 3초 미만
- 비정상적인 조회수 패턴

---

### Agent 3: Growth Experiment (A/B Testing)
**목적**: 데이터 기반 실험으로 미션 성과 최적화

**노드 구성 (Part 1 - User Assignment)**:
```
Webhook (POST /mission-click)
    ↓
A/B Group Assignment (Code - MD5 Hash)
    ↓
Route by Group (Switch)
    ├→ Group A: Emotional Copy
    └→ Group B: Reward Copy
           ↓
    Respond to Webhook
```

**노드 구성 (Part 2 - Daily Report)**:
```
Schedule Trigger (9AM)
    ↓
Aggregate Experiment Data (Code)
    ↓
AI Statistical Analysis (GPT-4)
    ↓
Generate Report (Code)
    ↓
Slack: Growth Report (#growth-experiments)
```

**A/B 그룹 설정**:
- **Group A (Control)**: "당신의 재능을 세상에 보여주세요" (감성 소구)
- **Group B (Test)**: "이 영상 하나로 $50 벌기" (보상 소구)

**통계 분석**:
- Z-Score 계산
- P-Value 기반 유의성 검증
- 95%/99% 신뢰수준 판단

---

### Agent 4: Business Intelligence (WBR)
**목적**: 주간 비즈니스 리뷰 자동화

**노드 구성**:
```
Schedule Trigger (Monday 8AM)
    ├→ Get Revenue Data (HTTP)
    ├→ Get Creator Metrics (HTTP)
    └→ Get Mission Metrics (HTTP)
           ↓
    Aggregate WBR Data (Code)
           ↓
    AI Business Analyst (GPT-4)
           ↓
    Generate WBR Report (Code)
           ↓
    ├→ Slack: WBR Report (#weekly-business-review)
    └→ Email: Executive Report
```

**리포트 포함 내용**:
- Executive Summary
- Health Scores (Overall, Revenue, Creators, Missions, Risk)
- Key Metrics (Payout, WAU, CPV, Fraud Blocked)
- Alerts & Action Items
- Top Performers
- Next Week Forecast

---

## ⚙️ Configuration Checklist

### Required Environment Variables
```env
# OpenAI
OPENAI_API_KEY=sk-xxx

# Slack
SLACK_BOT_TOKEN=xoxb-xxx

# Gmail (for WBR executive report)
GMAIL_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=xxx
```

### Slack Channels to Create
- `#market-insights` - Market opportunity alerts
- `#risk-alerts` - Fraud detection alerts
- `#settlements` - Approved settlement logs
- `#growth-experiments` - A/B test reports
- `#weekly-business-review` - WBR reports

### API Endpoints to Replace
| Mock URL | Replace With |
|----------|--------------|
| `jsonplaceholder.typicode.com` | Your actual API endpoints |
| `your-storage.com/reports/` | Your storage service (S3, GCS, etc.) |
| `track.example.com/exp/` | Your analytics tracking pixel |

---

## 🔧 Troubleshooting

### Workflow Import 실패
1. n8n 버전 확인 (권장: 1.0.0+)
2. JSON 파일 인코딩 확인 (UTF-8)
3. 노드 타입 호환성 확인

### AI Agent 노드 오류
1. OpenAI API Key 유효성 확인
2. API 사용량 한도 확인
3. 모델명 확인 (`gpt-4-turbo`)

### Slack 메시지 전송 실패
1. Bot Token 권한 확인 (`chat:write`, `channels:read`)
2. 채널에 Bot 초대 여부 확인
3. 채널명 정확성 확인 (`#` 포함)

---

## 📊 Expected Outcomes

| Metric | Current (Manual) | Target (Automated) | Impact |
|--------|-----------------|-------------------|--------|
| Market Analysis | 4시간/주 | 자동화 | -90% 시간 절약 |
| Settlement Process | 수동 검증 | 90%+ 자동화 | OpEx -70% |
| Fraud Detection | 사후 대응 | 실시간 탐지 | Risk Zero |
| A/B Testing | 월 1회 | 주 2회+ | Growth +15% |
| WBR Report | 반일 작업 | 자동 생성 | PM 생산성 향상 |

---

## 📝 Next Steps

1. **Phase 1**: Mock 데이터로 워크플로우 테스트
2. **Phase 2**: 실제 API 연동 (TikTok, Database)
3. **Phase 3**: Small Batch 크리에이터 대상 실험
4. **Phase 4**: Full Production 배포

---

## 📚 References

- [n8n Documentation](https://docs.n8n.io/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Slack API](https://api.slack.com/)
- [Project Piehands Requirements](../DETAILED_REQUIREMENTS.md)
- [Implementation Guide](../IMPLEMENTATION_GUIDE.md)

---

*Generated by n8n MCP Integration - Project Piehands*
