# Project Piehands - New User Setup Guide

> **Purpose**: 신규 팀원이 로컬 환경에서 n8n과 Slack을 연동하여 즉시 개발을 시작할 수 있도록 돕는 상세 가이드입니다.
> **Environment**: Windows (Docker Desktop), HTTP (Localhost), Slack Bot Token

---

## 🐳 1. Docker Environment Setup

### 1.1 Docker Desktop 설치
1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) 다운로드 및 설치
2. 설치 완료 후 Docker Desktop 실행 (WSL 2 backend 권장)

### 1.2 `docker-compose.yml` 설정
프로젝트 루트(`n8n/`)에 있는 `docker-compose.yml` 파일이 다음 설정을 포함하는지 확인하세요.
(HTTPS 대신 HTTP를 사용하여 로컬 연결 문제를 최소화했습니다.)

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n-virality
    restart: always
    ports:
      - "5678:5678"  # 호스트 포트:컨테이너 포트
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - GENERIC_TIMEZONE=Asia/Seoul
      - N8N_SECURE_COOKIE=false
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
    external: true
```

### 1.3 실행
터미널에서 다음 명령어로 n8n을 실행합니다.

```bash
# n8n 데이터 볼륨 생성 (최초 1회)
docker volume create n8n_data

# 컨테이너 실행
docker-compose up -d
```

브라우저에서 `http://localhost:5678` 접속하여 n8n 대시보드가 뜨는지 확인합니다.

---

## 🤖 2. Slack App Configuration

n8n이 Slack으로 알림을 보내거나 메시지를 읽으려면 Slack App 설정이 필요합니다.

### 2.1 Slack App 생성
1. [Slack API Apps](https://api.slack.com/apps) 접속 -> **Create New App** 클릭
2. **From scratch** 선택
3. **App Name**: `Piehands-Agent` (원하는 이름)
4. **Development Workspace**: 본인의 워크스페이스 선택

### 2.2 Bot Permissions 설정 (OAuth & Permissions)
좌측 메뉴 **Features > OAuth & Permissions** 로 이동하여 **Scopes > Bot Token Scopes**에 다음 권한을 추가합니다.

- `chat:write`: 채널에 메시지 쓰기 (필수)
- `chat:write.public`: 초대받지 않은 공개 채널에도 쓰기 (선택)
- `files:write`: 리포트(PDF 등) 업로드 (선택)
- `channels:read`: 채널 목록 조회 (선택)

### 2.3 App Install & Token 발급
1. 같은 페이지 상단의 **OAuth Tokens for Your Workspace** 섹션에서 **Install to Workspace** 클릭
2. 권한 승인 후 생성된 **Bot User OAuth Token** (`xoxb-`로 시작)을 복사합니다.
   > ⚠️ 이 토큰은 비밀번호와 같습니다. 절대 외부에 노출하지 마세요.

### 2.4 채널에 앱 초대
Slack 워크스페이스에서 알림을 받을 채널(예: `#alerts`)로 이동하여 앱을 초대합니다.
```text
/invite @Piehands-Agent
```

---

## 🔗 3. n8n Credential Setup

n8n에서 Slack과 LLM을 사용하기 위한 자격 증명(Credential)을 설정합니다.

### 3.1 Slack Credential 추가
1. n8n 대시보드 좌측 메뉴 **Credentials** -> **Add Credential**
2. **Slack API** 검색
3. **Authentication**: `Access Token` 선택
4. **Access Token**: 위에서 복사한 `xoxb-...` 토큰 입력
5. **Save** 클릭

### 3.2 OpenAI / Anthropic Credential 추가
1. **Credentials** -> **Add Credential**
2. **OpenAI** 또는 **Anthropic** 검색
3. API Key 입력 (각 서비스 대시보드에서 발급)
4. **Save** 클릭

---

## 🚀 4. Workflow Testing

이제 모든 준비가 되었습니다! 간단한 테스트 워크플로우를 만들어 봅니다.

1. **New Workflow** 생성
2. **Manual Trigger** 노드 추가 (테스트용)
3. **Slack** 노드 추가
   - **Credential**: 방금 만든 Slack 계정 선택
   - **Resource**: `Message`
   - **Operation**: `Post`
   - **Channel**: `#alerts` (또는 본인 채널명)
   - **Text**: `Hello from Project Piehands Agent! 🚀`
4. **Execute Workflow** 클릭
5. Slack 채널에 메시지가 오는지 확인

---

## ❓ Troubleshooting

**Q. n8n 접속이 안 돼요.**
- Docker가 실행 중인지 확인하세요 (`docker ps`).
- 포트 5678이 다른 프로그램에서 사용 중인지 확인하세요.

**Q. Slack 메시지가 안 와요.**
- 봇이 해당 채널에 초대되었는지 확인하세요 (`/invite`).
- `chat:write` 권한이 있는지 확인하고, 권한 변경 후에는 반드시 **Reinstall App**을 해야 합니다.

**Q. Webhook URL 에러가 나요.**
- 로컬 환경(localhost)에서는 외부 서비스(Slack Event 등)가 내 컴퓨터로 직접 신호를 보낼 수 없습니다.
- 이 경우 `n8n tunnel`을 사용하거나, 단순히 Polling 방식(주기적 확인)이나 Outbound 메시지 전송만 테스트하는 것을 권장합니다.
