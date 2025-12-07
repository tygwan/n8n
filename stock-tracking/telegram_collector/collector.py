"""
Telegram Channel Collector
- Telethon (User API)를 사용하여 채널 메시지 수집
- SQLite에 저장 + n8n Webhook으로 고우선순위 전송
- Interactive 채널 선택
"""

import asyncio
import os
import sys
import re
import httpx
from datetime import datetime
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import Channel, Chat

import database as db

# .env 파일 로드
load_dotenv()

# ============================================
# 설정
# ============================================
API_ID = 25052785
API_HASH = "e1f62a4e36c59b2d326f576f470ce95c"
SESSION_NAME = "telegram_collector"

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/telegram-collector")
SEND_HIGH_PRIORITY_TO_N8N = True  # priority >= 4만 n8n으로 전송

# ============================================
# 유틸리티
# ============================================
def log(msg):
    print(msg, flush=True)

async def send_to_n8n(data: dict):
    """n8n Webhook으로 데이터 전송 (고우선순위만)"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            response = await http_client.post(
                N8N_WEBHOOK_URL,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                log(f"  → n8n 전송 완료")
            else:
                log(f"  → n8n 전송 실패: {response.status_code}")
    except Exception as e:
        log(f"  → n8n 오류: {e}")

def analyze_message(text: str) -> dict:
    """메시지 분석 - 티커, 감성, 우선순위, 테마"""

    # 티커 추출
    us_pattern = r'\b[A-Z]{1,5}\b'
    kr_pattern = r'\b\d{6}\b'
    common_words = {'I', 'A', 'THE', 'AND', 'OR', 'IS', 'IT', 'TO', 'FOR', 'IN', 'ON', 'AT', 'BY', 'BE', 'AS', 'AN', 'IF', 'SO', 'UP', 'OUT', 'ALL', 'BUT', 'NOT', 'GET', 'HAS', 'HAD', 'HER', 'HIS', 'HOW', 'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'WAY', 'WHO', 'DID', 'OUR', 'PUT', 'SAY', 'SHE', 'TOO', 'USE'}

    us_tickers = [t for t in re.findall(us_pattern, text.upper()) if t not in common_words]
    kr_tickers = re.findall(kr_pattern, text)
    all_tickers = us_tickers + kr_tickers

    # 감성 분석
    buy_keywords = ['매수', 'buy', 'long', '진입', '추천', '상승', 'bullish', '강력매수', '급등']
    sell_keywords = ['매도', 'sell', 'short', '청산', '하락', 'bearish', '손절', '급락']
    alert_keywords = ['급등', '급락', '돌파', '폭등', '폭락', 'breaking', 'alert', '긴급', '신고가', '신저가', '속보']

    text_lower = text.lower()
    buy_score = sum(1 for k in buy_keywords if k.lower() in text_lower)
    sell_score = sum(1 for k in sell_keywords if k.lower() in text_lower)
    has_alert = any(k.lower() in text_lower for k in alert_keywords)

    sentiment = 'buy' if buy_score > sell_score else 'sell' if sell_score > buy_score else 'neutral'

    # 우선순위 (1-5)
    priority = 1
    if len(all_tickers) > 0:
        priority = 2
    if len(all_tickers) > 0 and sentiment != 'neutral':
        priority = 3
    if has_alert and len(all_tickers) > 0:
        priority = 4
    if has_alert and len(all_tickers) > 0 and ('급등' in text or '급락' in text):
        priority = 5

    # 테마 분류
    themes = db.classify_themes(text)

    return {
        'tickers': ','.join(all_tickers),
        'ticker_count': len(all_tickers),
        'sentiment': sentiment,
        'priority': priority,
        'themes': ','.join(themes) if themes else None
    }

# ============================================
# 채널 선택
# ============================================
def parse_numbers(text: str, max_val: int) -> set:
    """번호 파싱 (1,3,5 또는 1-5 형식)"""
    indices = set()
    for part in text.split(','):
        part = part.strip()
        if '-' in part:
            try:
                start, end = part.split('-')
                for i in range(int(start), int(end) + 1):
                    if 1 <= i <= max_val:
                        indices.add(i)
            except:
                pass
        elif part.isdigit():
            idx = int(part)
            if 1 <= idx <= max_val:
                indices.add(idx)
    return indices

def display_channels(all_channels: list, enabled_ids: set, blocked_ids: set):
    """채널 목록 표시"""
    log("\n" + "=" * 60)
    log("  채널 목록")
    log("=" * 60)

    for idx, ch in enumerate(all_channels, 1):
        if ch['id'] in blocked_ids:
            marker = "🚫"
            status = "[차단]"
        elif ch['id'] in enabled_ids:
            marker = "✅"
            status = ""
        else:
            marker = "○"
            status = ""

        username_str = f"(@{ch['username']})" if ch['username'] else ""
        log(f"  {marker} [{idx:2}] [{ch['type']:7}] {ch['name']} {username_str} {status}")

    log("=" * 60)

async def select_channels(client) -> list:
    """Interactive 채널 선택 및 관리"""

    log("\n📋 채널 목록 불러오는 중...")

    # 모든 채널/그룹 수집
    all_channels = []
    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, (Channel, Chat)):
            is_channel = isinstance(entity, Channel) and entity.broadcast
            all_channels.append({
                'id': entity.id,
                'username': getattr(entity, 'username', None),
                'name': dialog.name,
                'type': 'Channel' if is_channel else 'Group'
            })

    if not all_channels:
        log("❌ 가입된 채널이 없습니다.")
        return []

    # DB에서 기존 설정 불러오기
    saved_channels = db.get_enabled_channels()
    enabled_ids = {ch['id'] for ch in saved_channels}
    blocked_ids = set()  # 차단된 채널

    # 첫 번째 표시
    display_channels(all_channels, enabled_ids, blocked_ids)

    log("")
    log("📌 명령어:")
    log("   all        - 모든 채널 선택")
    log("   1,3,5      - 번호로 선택")
    log("   1-10       - 범위로 선택")
    log("   s          - 저장된 설정 사용")
    log("   block 1,2  - 채널 차단 (수집 제외)")
    log("   unblock 1  - 차단 해제")
    log("   list       - 목록 다시 보기")
    log("   done       - 선택 완료 및 시작")
    log("")

    selected_channels = []
    selection_made = False

    while True:
        cmd = input("명령: ").strip().lower()

        if cmd == 'done':
            if not selection_made and not enabled_ids:
                log("⚠️ 선택된 채널이 없습니다. 'all' 또는 번호를 입력하세요.")
                continue
            break

        elif cmd == 'list':
            display_channels(all_channels, enabled_ids, blocked_ids)

        elif cmd == 's':
            if enabled_ids:
                blocked_ids.clear()
                log(f"✅ 저장된 설정 사용: {len(enabled_ids)}개 채널")
                selection_made = True
            else:
                log("⚠️ 저장된 설정이 없습니다.")

        elif cmd == 'all':
            enabled_ids = {ch['id'] for ch in all_channels} - blocked_ids
            log(f"✅ 모든 채널 선택: {len(enabled_ids)}개")
            selection_made = True

        elif cmd.startswith('block '):
            nums_str = cmd[6:].strip()
            indices = parse_numbers(nums_str, len(all_channels))
            for idx in indices:
                ch = all_channels[idx - 1]
                blocked_ids.add(ch['id'])
                enabled_ids.discard(ch['id'])
                log(f"   🚫 차단: {ch['name']}")
            selection_made = True

        elif cmd.startswith('unblock '):
            nums_str = cmd[8:].strip()
            indices = parse_numbers(nums_str, len(all_channels))
            for idx in indices:
                ch = all_channels[idx - 1]
                blocked_ids.discard(ch['id'])
                log(f"   ✅ 차단 해제: {ch['name']}")

        elif cmd:
            # 번호로 선택
            indices = parse_numbers(cmd, len(all_channels))
            if indices:
                for idx in indices:
                    ch = all_channels[idx - 1]
                    if ch['id'] not in blocked_ids:
                        enabled_ids.add(ch['id'])
                log(f"✅ {len(indices)}개 채널 추가됨 (총 {len(enabled_ids)}개)")
                selection_made = True
            else:
                log("⚠️ 잘못된 명령입니다. 'list'로 목록을 확인하세요.")

    # 최종 선택된 채널
    selected_channels = [ch for ch in all_channels if ch['id'] in enabled_ids and ch['id'] not in blocked_ids]

    # DB에 저장
    for ch in all_channels:
        is_enabled = ch['id'] in enabled_ids and ch['id'] not in blocked_ids
        db.save_channel({**ch, 'enabled': is_enabled})

    log(f"\n✅ 최종 선택: {len(selected_channels)}개 채널")
    for ch in selected_channels:
        log(f"   - {ch['name']}")

    return [ch['id'] for ch in selected_channels]

# ============================================
# 과거 메시지 수집
# ============================================
async def backfill_messages(client, channel_ids: list, days: int = 14):
    """과거 메시지 백필 (기간 기반)"""
    from datetime import timedelta

    if not channel_ids:
        return

    log(f"\n📥 과거 메시지 수집 설정")
    log(f"   기본값: 최근 {days}일")
    log("   다른 기간을 원하면 숫자 입력 (예: 7, 14, 30)")
    log("   건너뛰려면 'n' 입력")

    answer = input("기간(일): ").strip().lower()

    if answer == 'n':
        log("⏭️ 과거 메시지 수집을 건너뜁니다.")
        return

    if answer.isdigit():
        days = int(answer)

    # 수집 기간 계산
    min_date = datetime.now() - timedelta(days=days)
    log(f"\n📥 최근 {days}일간 메시지 수집 중... ({min_date.strftime('%Y-%m-%d')} ~ 현재)")

    total_saved = 0
    for channel_id in channel_ids:
        try:
            entity = await client.get_entity(channel_id)
            channel_name = getattr(entity, 'title', str(channel_id))
            log(f"   {channel_name}...")

            count = 0
            async for message in client.iter_messages(channel_id, limit=None):
                # 기간 체크 - 수집 기간 이전이면 중단
                if message.date.replace(tzinfo=None) < min_date:
                    break

                if not message.text:
                    continue

                analysis = analyze_message(message.text)

                data = {
                    'message_id': message.id,
                    'channel_id': channel_id,
                    'channel_name': channel_name,
                    'channel_username': getattr(entity, 'username', None),
                    'text': message.text,
                    'date': int(message.date.timestamp()),
                    'collected_at': datetime.now().isoformat(),
                    'has_media': message.media is not None,
                    **analysis
                }

                result = db.save_message(data)
                if result:
                    count += 1

            log(f"      → {count}개 저장")
            total_saved += count

        except Exception as e:
            log(f"      → 오류: {e}")

    log(f"\n✅ 총 {total_saved}개 과거 메시지 저장 완료 (최근 {days}일)")

# ============================================
# 메인
# ============================================
async def main():
    log("=" * 60)
    log("  Telegram Channel Collector")
    log("=" * 60)

    # DB 초기화
    db.init_database()

    # 클라이언트 생성 및 연결
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    log("\n⏳ Telegram 연결 중...")
    try:
        await asyncio.wait_for(client.connect(), timeout=30)
    except asyncio.TimeoutError:
        log("❌ 연결 타임아웃!")
        return

    if not await client.is_user_authorized():
        log("❌ 로그인 필요! login.bat을 먼저 실행하세요.")
        await client.disconnect()
        return

    me = await client.get_me()
    log(f"✅ 로그인됨: {me.first_name}")

    # 채널 선택
    target_channels = await select_channels(client)

    if not target_channels:
        # 기존 저장된 채널 사용
        saved = db.get_enabled_channels()
        if saved:
            target_channels = [ch['id'] for ch in saved]
            log(f"\n📌 저장된 설정 사용: {len(target_channels)}개 채널")
        else:
            log("\n⚠️ 선택된 채널이 없어 모든 채널에서 수집합니다.")

    # 과거 메시지 백필 (선택)
    await backfill_messages(client, target_channels)

    # 이벤트 핸들러 등록
    @client.on(events.NewMessage(chats=target_channels if target_channels else None))
    async def handler(event):
        if not event.is_channel and not event.is_group:
            return

        chat = await event.get_chat()
        message_text = event.raw_text or ""

        if not message_text:
            return

        channel_name = getattr(chat, 'title', 'Unknown')
        channel_id = chat.id
        channel_username = getattr(chat, 'username', None)

        # 분석
        analysis = analyze_message(message_text)

        # 데이터 구성
        data = {
            'message_id': event.id,
            'channel_id': channel_id,
            'channel_name': channel_name,
            'channel_username': channel_username,
            'text': message_text,
            'date': int(event.date.timestamp()),
            'collected_at': datetime.now().isoformat(),
            'has_media': event.media is not None,
            **analysis
        }

        # SQLite 저장
        result = db.save_message(data)

        if result:
            priority_icon = ['⬜', '🟦', '🟨', '🟧', '🟥'][min(analysis['priority'], 5) - 1]
            themes_str = f" [{analysis['themes']}]" if analysis['themes'] else ""
            log(f"{priority_icon} [{channel_name}]{themes_str} {message_text[:40]}...")

            # 고우선순위는 n8n으로도 전송
            if SEND_HIGH_PRIORITY_TO_N8N and analysis['priority'] >= 4:
                n8n_data = {
                    "source": "user_api",
                    "update_id": f"{channel_id}_{event.id}",
                    "channel_post": {
                        "message_id": event.id,
                        "chat": {
                            "id": channel_id,
                            "title": channel_name,
                            "username": channel_username,
                            "type": "channel" if event.is_channel else "supergroup"
                        },
                        "date": int(event.date.timestamp()),
                        "text": message_text
                    },
                    "message": None,
                    "collected_at": datetime.now().isoformat(),
                    "has_media": event.media is not None,
                    "channel_name": channel_name,
                    "priority": analysis['priority'],
                    "themes": analysis['themes']
                }
                await send_to_n8n(n8n_data)
        else:
            pass  # 중복 메시지

    # 상태 출력
    stats = db.get_stats()
    log(f"\n📊 현재 DB 상태:")
    log(f"   - 총 메시지: {stats['total_messages']}")
    log(f"   - 오늘 수집: {stats['today']}")

    log("\n" + "=" * 60)
    if target_channels:
        log(f"🎯 {len(target_channels)}개 채널에서 수집 중...")
    else:
        log("🎯 모든 채널에서 수집 중...")
    log(f"📡 n8n Webhook: {N8N_WEBHOOK_URL}")
    log(f"💾 SQLite: {db.DB_PATH}")
    log("👂 새 메시지 대기 중... (Ctrl+C로 종료)")
    log("=" * 60)
    log("")

    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("\n종료됨")
    except Exception as e:
        log(f"오류: {e}")
        sys.exit(1)
