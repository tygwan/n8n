# Project Piehands - Strategic Product & Business Agent Architecture


---

## 💼 Module 1: Market Insight & Strategy Agent
> **Objective**: 미국 시장 트렌드와 경쟁사를 분석하여 "이길 수밖에 없는" 미션 전략 수립

### Business Logic
- **Competitor Gap Analysis**: 경쟁사(타 인플루언서 플랫폼) 대비 우리가 파고들 수 있는 니치 마켓 발굴
- **Winning Case Extraction**: 실제 미국에서 터진 숏폼 사례를 분석하여 "성공 방정식" 도출 -> 미션화

### n8n Workflow Design
1.  **Trend Data Aggregation** (TikTok, IG Reels, YouTube Shorts)
2.  **LLM Strategic Analysis** (GPT-4-Turbo)
    -   *Prompt Focus*: "단순 트렌드 나열이 아닌, 마이크로 인플루언서가 진입 가능한 **Blue Ocean** 키워드 추출"
    -   *Output*: `Mission_Strategy_Brief.pdf` (PM이 바로 의사결정 가능한 형태)
3.  **Actionable Mission Generation**
    -   추출된 전략을 바탕으로 즉시 배포 가능한 '미션 카드' 생성

---

## 💰 Module 2: Reward & Settlement System (Monetization)
> **Objective**: 공정하고 투명한 보상으로 크리에이터를 락인(Lock-in)하되, 회사의 재무적 리스크(Fraud)는 원천 차단

### Business Logic
- **Dynamic Pricing Model**: 크리에이터 등급, 카테고리, 시즌 이슈에 따라 조회수 당 단가(RPM) 동적 책정
- **Fraud Detection System (FDS)**: 어뷰징(가짜 조회수, 봇) 탐지 및 자동 지급 보류
- **Compliance Check**: 미국 세무(W-9) 및 법적 요구사항 자동 검증

### n8n Workflow Design
#### 1. Reward Calculation Workflow
-   **Trigger**: Daily View Count Update
-   **Logic**:
    ```javascript
    // Dynamic Reward Logic
    const baseRate = 0.5; // $0.5 per 1K views
    const qualityMultiplier = creator.grade === 'S' ? 1.2 : 1.0;
    const categoryBonus = trend.isHot ? 1.1 : 1.0;
    
    let estimatedReward = views * (baseRate / 1000) * qualityMultiplier * categoryBonus;
    
    // Cap logic (예산 방어)
    if (estimatedReward > mission.budget_cap) estimatedReward = mission.budget_cap;
    ```

#### 2. Settlement & Risk Workflow
-   **Trigger**: Weekly Settlement Cycle
-   **Risk Check Node (LLM + Rule-based)**:
    -   조회수 급등 패턴 분석 (비정상적 스파이크 감지)
    -   댓글/좋아요 비율 분석 (Engagement Quality)
-   **Action**:
    -   `Low Risk`: 자동 이체 예약 (Stripe/PayPal API)
    -   `High Risk`: 정산 보류 및 운영팀 슬랙 알림 발송

---

## 🚀 Module 3: Growth Experimentation (A/B Testing)
> **Objective**: "주장"이 아닌 "데이터"로 증명. 1-2일 주기로 가설 검증 및 프로덕트 개선

### Business Logic
- **Hypothesis**: "미션 제목에 '$$ Reward'를 노출하면 클릭률이 10% 상승할 것이다."
- **Experiment**: User Group A (기존) vs User Group B (변경안)
- **Decision**: 승자(Winner) 안을 즉시 v0.3에 반영

### n8n Workflow Design
#### 1. Mission Recommendation Engine (A/B Test)
-   **Input**: Creator Profile, Past Performance
-   **Split Logic**:
    -   Group A: 감성적 카피 ("당신의 재능을 보여주세요")
    -   Group B: 보상 중심 카피 ("이 영상 하나로 $50 벌기")
-   **Tracking**: 클릭(Click), 미션 시작(Start), 제출(Submit) 로그 적재

#### 2. Automated Performance Report
-   **Trigger**: Daily 09:00 AM
-   **LLM Analysis**:
    -   A/B 그룹 간 Conversion Rate 비교
    -   통계적 유의성 검증 (Chi-square approximation via LLM)
-   **Output**: 슬랙 채널로 `[Daily Growth Report] 실험 결과: B안 승리 (CTR +15%)` 발송

---

## 📊 Module 4: Business Intelligence (BI) Reporter
> **Objective**: 팀 전체가 데이터 기반으로 움직이도록 핵심 지표를 시각화하고 인사이트 제공

### Business Logic
- **Weekly Business Review (WBR)** 자동화
- 크리에이터 생태계 건전성 모니터링

### n8n Workflow Design
1.  **Data Source Integration**: DB (Postgres), Analytics (Amplitude/GA), Payment (Stripe)
2.  **Insight Generation (Claude-3.5-Sonnet)**
    -   "지난주 대비 WAU가 5% 하락했습니다. 주요 원인은 '뷰티' 카테고리의 미션 부족으로 분석됩니다."
    -   "Action Item: 뷰티 카테고리 긴급 미션 소싱 필요"
3.  **Report Distribution**: PDF 생성 후 경영진 이메일/슬랙 발송

---

## 🛠️ Implementation Strategy (AI Driven Development)

### 1. Rapid Prototyping with Cursor & Claude Code
-   **Day 1**: n8n 워크플로우 설계 및 핵심 로직(JS) 구현
-   **Day 2**: 실제 데이터(또는 Mock Data) 주입 후 시뮬레이션, 결과 분석
-   **Day 3**: 배포 및 실제 크리에이터 대상 실험 (Small Batch)

### 2. MCP Integration for Seamless Ops
-   **Direct Control**: Claude Code 터미널에서 `run_settlement_check`, `generate_weekly_report` 등 핵심 비즈니스 로직 직접 실행 및 제어
-   **Live Debugging**: 문제 발생 시 로그 즉시 분석 및 Hotfix 배포

---

## ✅ Success Criteria (Definition of Done)

1.  **Automated Revenue Ops**: 정산 및 리워드 계산의 90% 이상 자동화 (수동 개입 최소화)
2.  **Data-Driven Growth**: 매주 최소 2건 이상의 A/B 테스트 수행 및 결과 리포트 자동 생성
3.  **Risk Zero**: 어뷰징 유저에 대한 오지급 0건 달성
4.  **Market Impact**: 타겟 틱톡커 100명 이상 온보딩 및 활성화 (초기 목표)
