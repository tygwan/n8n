# Project Piehands - Final n8n Implementation In-Depth Guide

> **Role**: Senior PM & Business Strategist
> **Purpose**: 비즈니스 임팩트를 창출하는 3대 핵심 에이전트(Market, Monetization, Growth)의 실전 구현 매뉴얼

---

## 🛠️ Environment Setup

### 1. Docker Compose Configuration
n8n과 MCP 서버를 연동하기 위한 최적화된 설정입니다.

```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - GENERIC_TIMEZONE=Asia/Seoul
      - N8N_PAYLOAD_SIZE_MAX=100
    volumes:
      - ./n8n_data:/home/node/.n8n
```

---

## 📈 Agent 1: Market Insight (Blue Ocean Finder)

### 1. Workflow Logic
경쟁사가 놓친 기회를 포착하기 위해 **TikTok 트렌드**와 **경쟁사 데이터**를 교차 분석합니다.

### 2. Key Node Configuration

#### **A. HTTP Request (TikTok Trends)**
- **Method**: GET
- **URL**: `https://api.tiktok.com/v2/trends` (Simulation: Use Mocky.io)
- **Output**: `hashtags`, `growth_rate`

#### **B. LLM Node (Strategic Gap Analysis)**
- **Model**: GPT-4-Turbo
- **System Prompt**:
```markdown
당신은 10년차 마케팅 전략가입니다.
데이터 A(트렌드)와 데이터 B(경쟁사 커버리지)를 비교하여 **"Opportunity Gap"**을 찾으세요.

조건:
1. 트렌드 성장률(Growth Rate)이 상위 10%이지만,
2. 경쟁사 미션 수가 0개인 키워드를 찾을 것.
3. 해당 키워드로 마이크로 인플루언서가 찍을 수 있는 구체적 미션 시나리오를 제안할 것.
```

#### **C. Slack Node (Brief Report)**
- **Message**:
```text
🚀 [Market Opportunity Alert]
발견된 Blue Ocean 키워드: #{{$json.keyword}}
예상 도달 가능 조회수: {{$json.potential_views}}
추천 미션: {{$json.mission_title}}
👉 [전략 브리프 다운로드]({{$json.pdf_link}})
```

---

## 💰 Agent 2: Monetization & Risk (FDS)

### 1. Workflow Logic
조회수 기반 정산을 수행하되, **LLM을 활용한 FDS(이상 징후 탐지)**로 리스크를 방어합니다.

### 2. Key Node Configuration

#### **A. Function Node (Dynamic Pricing Logic)**
자바스크립트로 정교한 리워드 계산 로직을 구현합니다.

```javascript
// Input: views, creator_grade, seasonality_factor
const baseRate = 0.5; // $0.5 per 1K views

// 등급별 가중치
const gradeMultiplier = {
  'S': 1.5,
  'A': 1.2,
  'B': 1.0,
  'C': 0.8
};

// 시즌 이슈 (예: 블랙프라이데이)
const seasonMultiplier = $input.item.json.is_peak_season ? 1.3 : 1.0;

// 최종 리워드 산출
let finalReward = ($input.item.json.views / 1000) * baseRate * gradeMultiplier[$input.item.json.creator_grade] * seasonMultiplier;

// 예산 상한선(Cap) 적용
if (finalReward > 500) finalReward = 500;

return {
  json: {
    final_reward: finalReward.toFixed(2),
    calculation_detail: `Base(${baseRate}) * Grade(${gradeMultiplier[$input.item.json.creator_grade]}) * Season(${seasonMultiplier})`
  }
};
```

#### **B. LLM Node (Fraud Detection)**
- **Input**: 조회수 그래프(Time Series), 댓글 샘플
- **Prompt**:
```markdown
다음 조회수 그래프 패턴을 분석하여 '어뷰징(Abusing)' 확률을 0-100점으로 평가하세요.

[패턴 분석 기준]
1. 새벽 시간대(02:00-05:00)에 급격한 수직 상승이 있는가? (봇 의심)
2. 댓글이 "Good", "Nice" 등 단순 반복 패턴인가?
3. 시청 지속 시간(Retention)이 3초 미만인가?

결과 형식:
{
  "risk_score": 85,
  "reason": "새벽 3시에 1분 만에 1만 뷰 상승, 전형적인 봇 패턴 감지"
}
```

---

## 🚀 Agent 3: Growth Experiment (A/B Testing)

### 1. Workflow Logic
모든 미션 배포는 실험입니다. 유저를 A/B 그룹으로 나누고 승자(Winner)를 자동으로 판별합니다.

### 2. Key Node Configuration

#### **A. Function Node (User Hashing & Split)**
유저 ID를 기반으로 일관된 그룹 할당을 수행합니다.

```javascript
// Input: user_id
const crypto = require('crypto');
const hash = crypto.createHash('md5').update($input.item.json.user_id).digest('hex');

// 해시값의 첫 문자를 10진수로 변환하여 모듈러 연산
const segment = parseInt(hash.substring(0, 8), 16) % 100;

// 50:50 Split
const group = segment < 50 ? 'A' : 'B';

return {
  json: {
    user_id: $input.item.json.user_id,
    assigned_group: group,
    experiment_id: 'EXP_2024_MISSION_COPY'
  }
};
```

#### **B. Switch Node (Content Delivery)**
- **Condition**: `{{$json.assigned_group}}` Equal to `A`
- **Output A**: "당신의 재능을 보여주세요" (감성 소구)
- **Output B**: "이 영상 하나로 $50 벌기" (보상 소구)

#### **C. LLM Node (Statistical Analysis)**
- **Input**: A/B 그룹별 Conversion Data
- **Prompt**:
```markdown
실험 결과:
- Group A (감성): 노출 1000, 클릭 50 (CTR 5.0%)
- Group B (보상): 노출 1000, 클릭 80 (CTR 8.0%)

두 그룹 간의 차이가 통계적으로 유의미한지(95% 신뢰수준) 판단하고,
다음 버전(v0.3)에 어떤 카피를 채택해야 할지 PM에게 조언하세요.
```

---

## 📊 Business Intelligence Dashboard

### 1. Automated WBR (Weekly Business Review)
- **Trigger**: 매주 월요일 08:00
- **Data Sources**: Postgres (Revenue), Amplitude (Retention)
- **Output**: PDF Report via Slack

### 2. Key Metrics to Track
- **WAU (Weekly Active Users)**: 실제 미션에 참여 중인 크리에이터 수
- **CPV (Cost Per View)**: 브랜드가 지불하는 조회수 당 비용 (낮을수록 좋음)
- **Fraud Block Rate**: FDS가 방어한 금액 ($)

---

## ✅ Implementation Checklist

- [ ] **Docker**: n8n 컨테이너 실행 및 포트 포워딩 확인
- [ ] **API Keys**: OpenAI/Anthropic API 키 `.env` 설정
- [ ] **Database**: Postgres 연결 및 초기 스키마 생성
- [ ] **Validation**: 각 에이전트별 Test Run 수행 및 결과 로그 확인

이 가이드를 통해 **Project Piehands**의 기술적 구현뿐만 아니라, **사업적 성과를 증명하는 시스템**을 구축할 수 있습니다.
