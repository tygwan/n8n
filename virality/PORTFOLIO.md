# Project Piehands - Strategic AI Agent Portfolio

> **Applicant**: Senior PM & Business Strategist Candidate
> **Mission**: "Make Viral Content Accessible & Profitable for Micro-TikTokers"

---

## 1. Problem Definition (Why This Matters)

### 📉 The Pain Points
1.  **Creator**: "매일 뭘 찍어야 할지 모르겠고(Idea Block), 조회수가 나와도 돈이 안 된다(Monetization Gap)."
2.  **Brand**: "메가 인플루언서는 너무 비싸고, 마이크로 인플루언서는 관리가 불가능하다(Scalability Issue)."
3.  **Platform**: "단순 중개만으로는 리텐션을 유지할 수 없다. **'돈이 되는 경험'**을 줘야 한다."

### 🎯 The Strategic Goal
단순한 매칭 플랫폼이 아닌, **"크리에이터의 수익을 책임지는 AI 파트너"**로 진화해야 합니다.
이를 위해 **Market Insight(기회 포착) → Monetization(수익화) → Growth(성장)**의 선순환 구조를 AI 에이전트로 구축했습니다.

---

## 2. Solution: The "Profit-First" Agent System

저는 이 문제를 해결하기 위해 **3가지 핵심 AI 에이전트**를 설계하고 구현했습니다.

### 📈 Agent 1: Market Insight (Blue Ocean Finder)
> *"경쟁사가 놓친 기회를 훔쳐옵니다."*

-   **Function**: TikTok 트렌드와 경쟁사 데이터를 교차 분석하여 **'Opportunity Gap'** 발굴
-   **Impact**: PM의 감에 의존하던 기획을 **데이터 기반 전략**으로 전환
-   **Output**: [Market Opportunity Brief 예시](BUSINESS_REPORTS_EXAMPLE.md#3-market-opportunity-brief-strategy)

### 💰 Agent 2: Monetization & Risk Shield
> *"열심히 한 만큼 보상하되, 어뷰징은 1원도 용납하지 않습니다."*

-   **Function**:
    -   **Dynamic Pricing**: 크리에이터 등급/시즌에 따른 조회수 단가 최적화
    -   **AI FDS**: 조회수 그래프 패턴을 분석하여 어뷰징(Bot) 원천 차단
-   **Impact**: 예산 누수 **0%** 달성 및 크리에이터 신뢰도 확보
-   **Logic**: [Implementation Guide - Monetization](IMPLEMENTATION_GUIDE.md#agent-2-monetization--risk-fds)

### 🚀 Agent 3: Growth Experiment (A/B Testing)
> *"주장이 아닌 실험으로 증명합니다."*

-   **Function**: 미션 카피/보상 구조에 대한 실시간 A/B 테스트 및 승자 자동 판별
-   **Impact**: 미션 클릭률(CTR) **+4.0%p** 개선 (실험 결과 기반)
-   **Report**: [Growth Experiment Report 예시](BUSINESS_REPORTS_EXAMPLE.md#1-growth-experiment-report-ab-test)

---

## 3. Technical Architecture (AI Driven Development)

이 모든 시스템은 **n8n + LLM (GPT-4/Claude) + MCP** 기반으로 구축되어, **1-2일 단위의 빠른 실험 사이클**이 가능합니다.

-   **Workflow Engine**: n8n (Dockerized)
-   **Intelligence**: OpenAI GPT-4 Turbo (Strategy), Claude 3.5 Sonnet (Analysis)
-   **Ops Control**: Custom MCP Server for Direct Business Logic Execution

👉 [상세 구현 가이드 (Implementation Guide)](IMPLEMENTATION_GUIDE.md)
👉 [상세 요구사항 명세서 (Detailed Requirements)](DETAILED_REQUIREMENTS.md)

---

## 4. Expected Business Impact

이 시스템 도입 시 예상되는 1분기 성과입니다.

| Metric | Current (As-Is) | Target (To-Be) | Impact |
| :--- | :---: | :---: | :---: |
| **Creator Activation** | 15% | **35%** | **+20%p** (맞춤형 미션 제안) |
| **OpEx (운영 비용)** | High (수동 정산) | **Low** | **-70%** (정산/리스크 자동화) |
| **Fraud Loss** | 5% (추정) | **< 0.1%** | **Risk Zero** (AI FDS 도입) |

---

저는 **"코드로 전략을 구현하고, 데이터로 성과를 증명하는"** Senior PM입니다.
Project Piehands가 미국 시장을 장악하는 여정에 이 시스템이 강력한 무기가 될 확신합니다.
