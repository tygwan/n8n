# Project Piehands - Business & Growth Reports (Portfolio Assets)

> **Role**: Senior PM & Business Strategist
> **Purpose**: 실제 업무에서 사용되는 데이터 기반 의사결정 리포트 예시 (포트폴리오 증빙용)

---

## 📑 1. Growth Experiment Report (A/B Test)

### 🧪 Experiment: Mission Copy Optimization (v0.2)
**Date**: 2024-11-20 ~ 2024-11-22 (3 Days)
**Hypothesis**: "감성적 호소보다 **구체적 보상 금액($)**을 제목에 노출할 때, 미션 클릭률(CTR)이 10% 이상 상승할 것이다."

### 📊 Result Data (n8n Automated Aggregation)

| Metric | Group A (Control) | Group B (Test) | Lift (%) | Significance (p-value) |
| :--- | :---: | :---: | :---: | :---: |
| **Copy** | "당신의 재능을 보여주세요" | **"이 영상 하나로 $50 벌기"** | - | - |
| **Impressions** | 1,500 | 1,480 | - | - |
| **Clicks** | 75 | 133 | **+77.3%** | **< 0.001 (High)** |
| **CTR** | 5.0% | **9.0%** | **+4.0%p** | ✅ Significant |
| **Submissions** | 12 | 25 | +108% | < 0.01 |

### 💡 Insight & Action Item (LLM Generated)
1.  **Insight**: 크리에이터들은 '자아실현'보다 **'즉각적인 수익 기회'**에 훨씬 민감하게 반응함. 특히 $50이라는 구체적 숫자가 앵커링 효과(Anchoring Effect)를 준 것으로 분석됨.
2.  **Decision**: **Group B(보상 강조형) 카피를 Winner로 선정.**
3.  **Next Step**:
    -   v0.3 업데이트 시 모든 미션 제목을 '보상 강조형'으로 전면 교체.
    -   후속 실험: "$50 벌기" vs "최대 $100 벌기" (금액의 확실성 vs 규모) 테스트 제안.

---

## 📑 2. Weekly Business Review (WBR) - Monetization

### 📅 Period: 2024 Nov Week 3
**Summary**: 매출(GMV)은 전주 대비 **15% 성장**했으나, 어뷰징 시도가 **2건 감지**되어 FDS가 성공적으로 방어함.

### 💰 Key Metrics

-   **Total Payout**: $4,500 (WoW +15%)
-   **Avg. CPV (Cost Per View)**: $0.0008 (Target: < $0.001) ✅ **Healthy**
-   **Fraud Blocked**: $350 (2 Users)

### 🛡️ Risk Management Log (FDS)

| User ID | Detected Pattern | Risk Score | Action | Status |
| :--- | :--- | :---: | :---: | :--- |
| `@user_991` | **Bot Pattern**: 03:00 AM에 1분간 5,000 조회수 급등 | **92** | **Hold** | 🚫 Banned |
| `@user_102` | **Low Quality**: 댓글의 90%가 이모지(🔥) 단답형 | 45 | Review | ⚠️ Warning |

### 📝 Strategic Recommendation
-   **Issue**: 뷰티 카테고리의 CPV가 $0.0012로 다소 높음 (경쟁 심화).
-   **Strategy**: 뷰티 카테고리 전용 '보너스 챌린지'를 일시 중단하고, 효율이 좋은 '라이프스타일' 카테고리로 예산 20% 재배정 제안.

---

## 📑 3. Market Opportunity Brief (Strategy)

### 🚀 Blue Ocean Alert: "Desk Setup" Niche
**Analysis Date**: 2024-11-25

### 🔍 Opportunity Gap
-   **Trend Growth**: 🔥 +150% (Last 30 days)
-   **Competitor Coverage**: ❄️ Low (경쟁사 미션 0개)
-   **Keyword**: `#DeskSetup`, `#WFH`, `#TechMinimalist`

### 💡 Winning Formula (성공 방정식)
1.  **Hook**: "내 책상 위 $10짜리 아이템이 삶을 바꿨다" (가성비 강조)
2.  **Visual**: 어두운 조명 + 모니터 조명 (Cinematic B-roll)
3.  **Sound**: ASMR 타건음 or Lo-fi Beat

### 🎯 Proposed Mission
-   **Title**: "당신의 데스크테리어 꿀템을 소개하고 $30 받으세요"
-   **Target**: 테크/라이프스타일 남성 크리에이터 (10K-50K)
-   **Expected Viral Views**: 500K+

---

이 리포트들은 **n8n 워크플로우를 통해 데이터 수집부터 분석, 초안 작성까지 100% 자동화**되었습니다.
Senior PM은 이 초안을 바탕으로 최종 의사결정만 내리면 됩니다.
