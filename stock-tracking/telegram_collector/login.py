"""
Telegram Login Script
- 세션 파일 생성용 별도 로그인 스크립트
- 한 번 실행하면 telegram_collector.session 파일이 생성됨
"""

import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

# 설정
API_ID = 25052785
API_HASH = "e1f62a4e36c59b2d326f576f470ce95c"
SESSION_NAME = "telegram_collector"

async def login():
    print("=" * 50)
    print("  Telegram Login")
    print("=" * 50)
    print()

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"Already logged in as: {me.first_name} (@{me.username})")
        print("Session file exists. You can run collector.py now.")
        await client.disconnect()
        return

    # 전화번호 입력
    print("Enter your phone number (with country code):")
    print("Example: +821012345678")
    print()
    phone = input("Phone: ").strip()

    if not phone:
        print("Phone number is required!")
        await client.disconnect()
        return

    # 인증 코드 요청
    print()
    print("Sending login code...")
    await client.send_code_request(phone)

    # 인증 코드 입력
    print()
    print("Check your Telegram app for the login code.")
    code = input("Enter code: ").strip()

    try:
        await client.sign_in(phone, code)
    except SessionPasswordNeededError:
        # 2단계 인증이 설정된 경우
        print()
        print("Two-factor authentication is enabled.")
        password = input("Enter your 2FA password: ").strip()
        await client.sign_in(password=password)

    me = await client.get_me()
    print()
    print("=" * 50)
    print(f"  Login successful!")
    print(f"  User: {me.first_name} (@{me.username})")
    print("=" * 50)
    print()
    print("Session file created: telegram_collector.session")
    print("You can now run collector.py")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(login())
