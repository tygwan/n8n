"""
SQLite Database Module
- 텔레그램 메시지 저장 및 관리
- 테마별 분류 지원
- AI 분석 결과 저장
- 처리 로그 추적
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

# 데이터베이스 경로
DB_PATH = Path(__file__).parent / "data" / "telegram_messages.db"

def get_connection() -> sqlite3.Connection:
    """데이터베이스 연결"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """데이터베이스 초기화 - 테이블 생성"""
    conn = get_connection()
    cursor = conn.cursor()

    # 메시지 테이블 (AI 분석 필드 포함)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            channel_name TEXT,
            channel_username TEXT,
            text TEXT,
            date INTEGER,
            collected_at TEXT,
            has_media INTEGER DEFAULT 0,

            -- 기본 분석 결과
            tickers TEXT,
            ticker_count INTEGER DEFAULT 0,
            sentiment TEXT,
            priority INTEGER DEFAULT 1,
            themes TEXT,

            -- AI 분석 결과 (GPT-5-mini)
            ai_analyzed INTEGER DEFAULT 0,
            ai_theme_tags TEXT,
            ai_sentiment_tag TEXT,
            ai_summary TEXT,
            ai_key_facts TEXT,
            ai_investment_insight TEXT,
            ai_analyzed_at TEXT,
            slack_channels TEXT,

            -- 처리 상태
            status TEXT DEFAULT 'pending',
            processed_at TEXT,
            sent_to_n8n INTEGER DEFAULT 0,
            sent_to_sheets INTEGER DEFAULT 0,
            sent_to_slack INTEGER DEFAULT 0,

            -- 중복 방지
            UNIQUE(channel_id, message_id)
        )
    """)

    # 채널 설정 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT,
            type TEXT,
            enabled INTEGER DEFAULT 1,
            added_at TEXT,
            last_message_id INTEGER DEFAULT 0
        )
    """)

    # 테마 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS themes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            keywords TEXT,
            description TEXT,
            color TEXT,
            created_at TEXT
        )
    """)

    # 처리 로그 테이블 (상태 추적)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processing_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            step TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT,
            error_message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES messages(id)
        )
    """)

    # 기본 테마 추가
    default_themes = [
        ('반도체', 'SK하이닉스,삼성전자,마이크론,엔비디아,NVIDIA,AMD,반도체,HBM,DDR5,파운드리', '반도체 관련 종목'),
        ('2차전지', 'LG에너지,삼성SDI,CATL,테슬라,배터리,리튬,양극재,음극재,전고체', '2차전지/배터리 관련'),
        ('AI/빅테크', 'OpenAI,ChatGPT,MS,마이크로소프트,구글,메타,애플,아마존,AI,인공지능', 'AI 및 빅테크 기업'),
        ('바이오', '셀트리온,삼성바이오,신약,FDA,임상,바이오,제약,헬스케어', '바이오/제약 관련'),
        ('금융', '금리,연준,Fed,FOMC,인플레이션,CPI,고용,실업률,국채,달러', '금융/매크로 지표'),
        ('코인', '비트코인,이더리움,BTC,ETH,코인,크립토,가상자산,업비트,바이낸스', '암호화폐 관련'),
        ('IPO/공모', 'IPO,상장,공모,스팩,SPAC,청약', 'IPO 및 공모주'),
        ('배당', '배당,배당금,배당률,배당주,고배당', '배당 관련'),
    ]

    for name, keywords, desc in default_themes:
        cursor.execute("""
            INSERT OR IGNORE INTO themes (name, keywords, description, created_at)
            VALUES (?, ?, ?, ?)
        """, (name, keywords, desc, datetime.now().isoformat()))

    # 인덱스 생성
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_date ON messages(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_priority ON messages(priority)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_ai_analyzed ON messages(ai_analyzed)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_sent_to_slack ON messages(sent_to_slack)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_composite ON messages(status, ai_analyzed, date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_processing_log_message ON processing_log(message_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_processing_log_step ON processing_log(step, status)")

    conn.commit()
    conn.close()
    print(f"[OK] Database initialized: {DB_PATH}")

# ============================================
# 메시지 관련 함수
# ============================================

def save_message(data: Dict[str, Any]) -> Optional[int]:
    """메시지 저장 (중복 시 무시)"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO messages (
                message_id, channel_id, channel_name, channel_username,
                text, date, collected_at, has_media,
                tickers, ticker_count, sentiment, priority, themes, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('message_id'),
            data.get('channel_id'),
            data.get('channel_name'),
            data.get('channel_username'),
            data.get('text'),
            data.get('date'),
            data.get('collected_at'),
            1 if data.get('has_media') else 0,
            data.get('tickers'),
            data.get('ticker_count', 0),
            data.get('sentiment'),
            data.get('priority', 1),
            data.get('themes'),
            'pending'
        ))
        conn.commit()

        if cursor.rowcount > 0:
            return cursor.lastrowid
        return None  # 중복
    except Exception as e:
        print(f"[ERROR] DB Error: {e}")
        return None
    finally:
        conn.close()

def get_pending_messages(limit: int = 100) -> List[Dict]:
    """미처리 메시지 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM messages
        WHERE status = 'pending'
        ORDER BY priority DESC, date DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_messages_by_theme(theme: str, limit: int = 50) -> List[Dict]:
    """테마별 메시지 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM messages
        WHERE themes LIKE ?
        ORDER BY date DESC
        LIMIT ?
    """, (f'%{theme}%', limit))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def mark_as_processed(message_ids: List[int], sent_to_sheets: bool = False):
    """메시지 처리 완료 표시"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        UPDATE messages
        SET status = 'processed',
            processed_at = ?,
            sent_to_sheets = ?
        WHERE id IN ({','.join('?' * len(message_ids))})
    """, [datetime.now().isoformat(), 1 if sent_to_sheets else 0] + message_ids)

    conn.commit()
    conn.close()

def get_stats() -> Dict:
    """통계 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    stats = {}

    # 총 메시지 수
    cursor.execute("SELECT COUNT(*) FROM messages")
    stats['total_messages'] = cursor.fetchone()[0]

    # 상태별
    cursor.execute("SELECT status, COUNT(*) FROM messages GROUP BY status")
    stats['by_status'] = dict(cursor.fetchall())

    # 채널별
    cursor.execute("""
        SELECT channel_name, COUNT(*) as cnt
        FROM messages
        GROUP BY channel_id
        ORDER BY cnt DESC
        LIMIT 10
    """)
    stats['by_channel'] = dict(cursor.fetchall())

    # 우선순위별
    cursor.execute("SELECT priority, COUNT(*) FROM messages GROUP BY priority")
    stats['by_priority'] = dict(cursor.fetchall())

    # 오늘 수집
    cursor.execute("""
        SELECT COUNT(*) FROM messages
        WHERE date(collected_at) = date('now')
    """)
    stats['today'] = cursor.fetchone()[0]

    conn.close()
    return stats

# ============================================
# 채널 관련 함수
# ============================================

def save_channel(channel: Dict):
    """채널 정보 저장"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO channels (id, username, name, type, enabled, added_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        channel['id'],
        channel.get('username'),
        channel['name'],
        channel['type'],
        1 if channel.get('enabled', True) else 0,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

def get_enabled_channels() -> List[Dict]:
    """활성화된 채널 목록"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM channels WHERE enabled = 1")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_channel_status(channel_id: int, enabled: bool):
    """채널 활성화/비활성화"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE channels SET enabled = ? WHERE id = ?
    """, (1 if enabled else 0, channel_id))

    conn.commit()
    conn.close()

# ============================================
# AI 분석 관련 함수
# ============================================

def get_unanalyzed_messages(limit: int = 50, priority_first: bool = True) -> List[Dict]:
    """AI 미분석 메시지 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    order = "priority DESC, date DESC" if priority_first else "date DESC"
    cursor.execute(f"""
        SELECT * FROM messages
        WHERE ai_analyzed = 0 AND text IS NOT NULL AND text != ''
        ORDER BY {order}
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_ai_analysis(message_id: int, analysis: Dict[str, Any]) -> bool:
    """AI 분석 결과 업데이트"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE messages
            SET ai_analyzed = 1,
                ai_theme_tags = ?,
                ai_sentiment_tag = ?,
                ai_summary = ?,
                ai_key_facts = ?,
                ai_investment_insight = ?,
                ai_analyzed_at = ?,
                slack_channels = ?,
                status = 'analyzed'
            WHERE id = ?
        """, (
            analysis.get('theme_tags'),
            analysis.get('sentiment_tag'),
            analysis.get('summary'),
            analysis.get('key_facts'),
            analysis.get('investment_insight'),
            datetime.now().isoformat(),
            analysis.get('slack_channels'),
            message_id
        ))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"[ERROR] AI Analysis Update Error: {e}")
        return False
    finally:
        conn.close()

def mark_as_sent_to_slack(message_ids: List[int]) -> int:
    """Slack 전송 완료 표시"""
    if not message_ids:
        return 0

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
        UPDATE messages
        SET sent_to_slack = 1,
            status = 'completed',
            processed_at = ?
        WHERE id IN ({','.join('?' * len(message_ids))})
    """, [datetime.now().isoformat()] + message_ids)

    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected

def get_historical_messages(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    channel_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict]:
    """과거 데이터 조회 (필터링 지원)"""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM messages WHERE 1=1"
    params = []

    if start_date:
        query += " AND collected_at >= ?"
        params.append(start_date)
    if end_date:
        query += " AND collected_at <= ?"
        params.append(end_date)
    if channel_id:
        query += " AND channel_id = ?"
        params.append(channel_id)
    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ============================================
# 처리 상태 추적 함수
# ============================================

def update_message_status(message_id: int, status: str) -> bool:
    """메시지 상태 업데이트"""
    valid_statuses = ['pending', 'processing', 'analyzed', 'sent', 'completed', 'failed']
    if status not in valid_statuses:
        print(f"[ERROR] Invalid status: {status}")
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE messages SET status = ? WHERE id = ?
    """, (status, message_id))

    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def log_processing_step(message_id: int, step: str, status: str, details: str = None, error: str = None):
    """처리 단계 로깅"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO processing_log (message_id, step, status, details, error_message, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (message_id, step, status, details, error, datetime.now().isoformat()))

    conn.commit()
    conn.close()

def get_processing_status(message_id: int) -> Dict:
    """메시지 처리 상태 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    # 메시지 정보
    cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
    message = cursor.fetchone()

    # 처리 로그
    cursor.execute("""
        SELECT * FROM processing_log
        WHERE message_id = ?
        ORDER BY created_at DESC
    """, (message_id,))
    logs = cursor.fetchall()

    conn.close()

    if not message:
        return None

    return {
        'message': dict(message),
        'logs': [dict(log) for log in logs]
    }

def get_processing_stats() -> Dict:
    """처리 통계 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    stats = {}

    # 상태별 카운트
    cursor.execute("""
        SELECT status, COUNT(*) as cnt FROM messages GROUP BY status
    """)
    stats['by_status'] = dict(cursor.fetchall())

    # AI 분석 현황
    cursor.execute("SELECT COUNT(*) FROM messages WHERE ai_analyzed = 1")
    stats['ai_analyzed'] = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM messages WHERE ai_analyzed = 0")
    stats['ai_pending'] = cursor.fetchone()[0]

    # Slack 전송 현황
    cursor.execute("SELECT COUNT(*) FROM messages WHERE sent_to_slack = 1")
    stats['sent_to_slack'] = cursor.fetchone()[0]

    # 오늘 처리량
    cursor.execute("""
        SELECT COUNT(*) FROM messages
        WHERE date(processed_at) = date('now')
    """)
    stats['processed_today'] = cursor.fetchone()[0]

    # 최근 7일 처리량
    cursor.execute("""
        SELECT date(processed_at) as day, COUNT(*) as cnt
        FROM messages
        WHERE processed_at >= date('now', '-7 days')
        GROUP BY date(processed_at)
        ORDER BY day DESC
    """)
    stats['daily_processed'] = dict(cursor.fetchall())

    conn.close()
    return stats

# ============================================
# 테마 관련 함수
# ============================================

def get_themes() -> List[Dict]:
    """테마 목록 조회"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM themes")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def classify_themes(text: str) -> List[str]:
    """텍스트에서 테마 분류"""
    themes = get_themes()
    matched = []

    text_lower = text.lower()
    for theme in themes:
        keywords = theme['keywords'].lower().split(',')
        for keyword in keywords:
            if keyword.strip() in text_lower:
                matched.append(theme['name'])
                break

    return matched

# ============================================
# 마이그레이션 함수
# ============================================

def migrate_database():
    """기존 데이터베이스에 새 컬럼 추가 (마이그레이션)"""
    conn = get_connection()
    cursor = conn.cursor()

    # 새 컬럼 목록
    new_columns = [
        ("ai_analyzed", "INTEGER DEFAULT 0"),
        ("ai_theme_tags", "TEXT"),
        ("ai_sentiment_tag", "TEXT"),
        ("ai_summary", "TEXT"),
        ("ai_key_facts", "TEXT"),
        ("ai_investment_insight", "TEXT"),
        ("ai_analyzed_at", "TEXT"),
        ("slack_channels", "TEXT"),
        ("sent_to_slack", "INTEGER DEFAULT 0"),
    ]

    # 기존 컬럼 확인
    cursor.execute("PRAGMA table_info(messages)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # 없는 컬럼만 추가
    added = []
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE messages ADD COLUMN {col_name} {col_type}")
                added.append(col_name)
            except Exception as e:
                print(f"[WARN] Column {col_name} migration warning: {e}")

    # processing_log 테이블 생성 (없으면)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processing_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            step TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT,
            error_message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (message_id) REFERENCES messages(id)
        )
    """)

    # 새 인덱스 추가
    new_indexes = [
        ("idx_messages_ai_analyzed", "messages(ai_analyzed)"),
        ("idx_messages_sent_to_slack", "messages(sent_to_slack)"),
        ("idx_messages_composite", "messages(status, ai_analyzed, date)"),
        ("idx_processing_log_message", "processing_log(message_id)"),
        ("idx_processing_log_step", "processing_log(step, status)"),
    ]

    for idx_name, idx_def in new_indexes:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_def}")
        except Exception as e:
            print(f"[WARN] Index {idx_name} warning: {e}")

    conn.commit()
    conn.close()

    if added:
        print(f"[OK] Migration completed. Added columns: {', '.join(added)}")
    else:
        print("[OK] Database schema is up to date")

    return added

# ============================================
# 초기화
# ============================================

if __name__ == "__main__":
    # 먼저 마이그레이션 실행 (기존 DB가 있을 경우 새 컬럼 추가)
    migrate_database()
    # 그 다음 초기화 (새 테이블/인덱스 생성)
    init_database()
    print("\n📊 Stats:", get_stats())
    print("📊 Processing Stats:", get_processing_stats())
