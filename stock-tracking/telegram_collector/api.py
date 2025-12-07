"""
API Server for n8n Integration
- SQLite 데이터 조회/관리 API
- n8n에서 HTTP Request로 호출
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

import database as db

# FastAPI 앱
app = FastAPI(
    title="Telegram Collector API",
    description="n8n 연동을 위한 SQLite 데이터 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Models
# ============================================
class ProcessRequest(BaseModel):
    message_ids: List[int]
    sent_to_sheets: bool = False

class ThemeCreate(BaseModel):
    name: str
    keywords: str
    description: Optional[str] = None

class AIAnalysisResult(BaseModel):
    theme_tags: Optional[str] = None
    sentiment_tag: Optional[str] = None
    summary: Optional[str] = None
    key_facts: Optional[str] = None
    investment_insight: Optional[str] = None
    slack_channels: Optional[str] = None

class StatusUpdate(BaseModel):
    status: str

class SlackSentRequest(BaseModel):
    message_ids: List[int]

# ============================================
# 메시지 API
# ============================================

@app.get("/")
def root():
    """API 상태 확인"""
    return {"status": "ok", "service": "Telegram Collector API"}

@app.get("/messages/pending")
def get_pending_messages(
    limit: int = Query(100, ge=1, le=1000),
    min_priority: int = Query(1, ge=1, le=5)
):
    """미처리 메시지 조회 (n8n 배치 처리용)"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM messages
        WHERE status = 'pending' AND priority >= ?
        ORDER BY priority DESC, date DESC
        LIMIT ?
    """, (min_priority, limit))

    rows = cursor.fetchall()
    conn.close()

    return {
        "count": len(rows),
        "messages": [dict(row) for row in rows]
    }

@app.get("/messages/by-theme/{theme}")
def get_messages_by_theme(
    theme: str,
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = None
):
    """테마별 메시지 조회"""
    conn = db.get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM messages WHERE themes LIKE ?"
    params = [f'%{theme}%']

    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY date DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return {
        "theme": theme,
        "count": len(rows),
        "messages": [dict(row) for row in rows]
    }

@app.get("/messages/by-ticker/{ticker}")
def get_messages_by_ticker(
    ticker: str,
    limit: int = Query(50, ge=1, le=500)
):
    """티커별 메시지 조회"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM messages
        WHERE tickers LIKE ?
        ORDER BY date DESC
        LIMIT ?
    """, (f'%{ticker.upper()}%', limit))

    rows = cursor.fetchall()
    conn.close()

    return {
        "ticker": ticker.upper(),
        "count": len(rows),
        "messages": [dict(row) for row in rows]
    }

@app.get("/messages/recent")
def get_recent_messages(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(100, ge=1, le=1000)
):
    """최근 N시간 메시지"""
    conn = db.get_connection()
    cursor = conn.cursor()

    since = datetime.now() - timedelta(hours=hours)

    cursor.execute("""
        SELECT * FROM messages
        WHERE collected_at >= ?
        ORDER BY date DESC
        LIMIT ?
    """, (since.isoformat(), limit))

    rows = cursor.fetchall()
    conn.close()

    return {
        "hours": hours,
        "count": len(rows),
        "messages": [dict(row) for row in rows]
    }

@app.post("/messages/process")
def mark_messages_processed(request: ProcessRequest):
    """메시지 처리 완료 표시"""
    if not request.message_ids:
        raise HTTPException(status_code=400, detail="message_ids required")

    db.mark_as_processed(request.message_ids, request.sent_to_sheets)

    return {
        "processed": len(request.message_ids),
        "message_ids": request.message_ids
    }

# ============================================
# AI 분석 API
# ============================================

@app.get("/messages/unanalyzed")
def get_unanalyzed_messages(
    limit: int = Query(50, ge=1, le=500),
    priority_first: bool = Query(True)
):
    """AI 미분석 메시지 조회 (n8n GPT 처리용)"""
    messages = db.get_unanalyzed_messages(limit, priority_first)
    return {
        "count": len(messages),
        "messages": messages
    }

@app.put("/messages/{message_id}/ai-analysis")
def update_ai_analysis(message_id: int, analysis: AIAnalysisResult):
    """AI 분석 결과 저장"""
    success = db.update_ai_analysis(message_id, analysis.dict())

    if not success:
        raise HTTPException(status_code=404, detail="Message not found")

    # 처리 로그 기록
    db.log_processing_step(message_id, "ai_analysis", "completed",
                          f"Tags: {analysis.theme_tags}, Sentiment: {analysis.sentiment_tag}")

    return {"updated": True, "message_id": message_id}

@app.get("/messages/analyzed")
def get_analyzed_messages(
    limit: int = Query(100, ge=1, le=500),
    sent_to_slack: Optional[bool] = None
):
    """AI 분석 완료 메시지 조회"""
    conn = db.get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM messages WHERE ai_analyzed = 1"
    params = []

    if sent_to_slack is not None:
        query += " AND sent_to_slack = ?"
        params.append(1 if sent_to_slack else 0)

    query += " ORDER BY ai_analyzed_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return {
        "count": len(rows),
        "messages": [dict(row) for row in rows]
    }

@app.post("/messages/sent-to-slack")
def mark_sent_to_slack(request: SlackSentRequest):
    """Slack 전송 완료 표시"""
    if not request.message_ids:
        raise HTTPException(status_code=400, detail="message_ids required")

    affected = db.mark_as_sent_to_slack(request.message_ids)

    # 각 메시지에 처리 로그 기록
    for msg_id in request.message_ids:
        db.log_processing_step(msg_id, "slack_send", "completed")

    return {
        "marked": affected,
        "message_ids": request.message_ids
    }

# ============================================
# 과거 데이터 처리 API
# ============================================

@app.get("/messages/historical")
def get_historical_messages(
    start_date: Optional[str] = Query(None, description="시작일 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="종료일 (YYYY-MM-DD)"),
    channel_id: Optional[int] = None,
    status: Optional[str] = Query(None, description="pending, processing, analyzed, completed"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """과거 데이터 조회 (필터링 지원)"""
    messages = db.get_historical_messages(
        start_date=start_date,
        end_date=end_date,
        channel_id=channel_id,
        status=status,
        limit=limit,
        offset=offset
    )

    return {
        "count": len(messages),
        "limit": limit,
        "offset": offset,
        "messages": messages
    }

@app.get("/messages/historical/unprocessed-count")
def get_unprocessed_historical_count():
    """미처리 과거 데이터 카운트"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN ai_analyzed = 0 THEN 1 ELSE 0 END) as ai_pending,
            SUM(CASE WHEN sent_to_slack = 0 AND ai_analyzed = 1 THEN 1 ELSE 0 END) as slack_pending
        FROM messages
    """)
    result = dict(cursor.fetchone())
    conn.close()

    return result

# ============================================
# 상태 관리 API
# ============================================

@app.put("/messages/{message_id}/status")
def update_message_status(message_id: int, status_update: StatusUpdate):
    """메시지 상태 업데이트"""
    success = db.update_message_status(message_id, status_update.status)

    if not success:
        raise HTTPException(status_code=400, detail="Invalid status or message not found")

    db.log_processing_step(message_id, "status_change", "completed",
                          f"New status: {status_update.status}")

    return {"updated": True, "message_id": message_id, "status": status_update.status}

@app.get("/processing-status/{message_id}")
def get_processing_status(message_id: int):
    """메시지 처리 상태 및 로그 조회"""
    result = db.get_processing_status(message_id)

    if not result:
        raise HTTPException(status_code=404, detail="Message not found")

    return result

# ============================================
# 통계 API
# ============================================

@app.get("/stats")
def get_stats():
    """전체 통계"""
    return db.get_stats()

@app.get("/stats/processing")
def get_processing_stats():
    """처리 현황 통계 (AI 분석 + Slack 전송)"""
    return db.get_processing_stats()

@app.get("/stats/themes")
def get_theme_stats():
    """테마별 통계"""
    conn = db.get_connection()
    cursor = conn.cursor()

    # 테마 목록
    themes = db.get_themes()

    stats = {}
    for theme in themes:
        cursor.execute("""
            SELECT COUNT(*) FROM messages
            WHERE themes LIKE ?
        """, (f'%{theme["name"]}%',))
        stats[theme['name']] = cursor.fetchone()[0]

    conn.close()

    return {
        "themes": stats,
        "total_themes": len(themes)
    }

@app.get("/stats/channels")
def get_channel_stats():
    """채널별 통계"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            channel_name,
            COUNT(*) as message_count,
            AVG(priority) as avg_priority,
            MAX(collected_at) as last_message
        FROM messages
        GROUP BY channel_id
        ORDER BY message_count DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return {
        "channels": [dict(row) for row in rows]
    }

@app.get("/stats/daily")
def get_daily_stats(days: int = Query(7, ge=1, le=30)):
    """일별 통계"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            date(collected_at) as date,
            COUNT(*) as count,
            AVG(priority) as avg_priority,
            SUM(CASE WHEN priority >= 4 THEN 1 ELSE 0 END) as high_priority
        FROM messages
        WHERE collected_at >= date('now', ?)
        GROUP BY date(collected_at)
        ORDER BY date DESC
    """, (f'-{days} days',))

    rows = cursor.fetchall()
    conn.close()

    return {
        "days": days,
        "daily": [dict(row) for row in rows]
    }

# ============================================
# 테마 API
# ============================================

@app.get("/themes")
def get_themes():
    """테마 목록"""
    return {"themes": db.get_themes()}

@app.post("/themes")
def create_theme(theme: ThemeCreate):
    """테마 추가"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO themes (name, keywords, description, created_at)
            VALUES (?, ?, ?, ?)
        """, (theme.name, theme.keywords, theme.description, datetime.now().isoformat()))
        conn.commit()
        return {"created": theme.name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

# ============================================
# 채널 API
# ============================================

@app.get("/channels")
def get_channels():
    """채널 목록"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM channels ORDER BY name")
    rows = cursor.fetchall()
    conn.close()

    return {"channels": [dict(row) for row in rows]}

@app.get("/channels/enabled")
def get_enabled_channels():
    """활성화된 채널"""
    return {"channels": db.get_enabled_channels()}

# ============================================
# 리포트 API (n8n 배치 처리용)
# ============================================

@app.get("/report/summary")
def get_summary_report(hours: int = Query(24, ge=1, le=168)):
    """요약 리포트 (n8n 슬랙 전송용)"""
    conn = db.get_connection()
    cursor = conn.cursor()

    since = datetime.now() - timedelta(hours=hours)

    # 기본 통계
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN priority >= 4 THEN 1 ELSE 0 END) as high_priority,
            AVG(priority) as avg_priority
        FROM messages
        WHERE collected_at >= ?
    """, (since.isoformat(),))
    stats = dict(cursor.fetchone())

    # 테마별
    cursor.execute("""
        SELECT themes, COUNT(*) as cnt
        FROM messages
        WHERE collected_at >= ? AND themes IS NOT NULL AND themes != ''
        GROUP BY themes
        ORDER BY cnt DESC
        LIMIT 5
    """, (since.isoformat(),))
    top_themes = cursor.fetchall()

    # 티커별
    cursor.execute("""
        SELECT tickers, COUNT(*) as cnt
        FROM messages
        WHERE collected_at >= ? AND ticker_count > 0
        GROUP BY tickers
        ORDER BY cnt DESC
        LIMIT 10
    """, (since.isoformat(),))
    top_tickers = cursor.fetchall()

    # 고우선순위 메시지
    cursor.execute("""
        SELECT channel_name, text, priority, themes, tickers
        FROM messages
        WHERE collected_at >= ? AND priority >= 4
        ORDER BY priority DESC, date DESC
        LIMIT 5
    """, (since.isoformat(),))
    alerts = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "period_hours": hours,
        "generated_at": datetime.now().isoformat(),
        "stats": stats,
        "top_themes": [{"theme": t[0], "count": t[1]} for t in top_themes],
        "top_tickers": [{"tickers": t[0], "count": t[1]} for t in top_tickers],
        "alerts": alerts
    }

# ============================================
# 실행
# ============================================

if __name__ == "__main__":
    import uvicorn

    # DB 초기화 및 마이그레이션
    db.init_database()
    db.migrate_database()

    print("🚀 API Server starting...")
    print("📖 Docs: http://localhost:8000/docs")
    print("📊 New endpoints:")
    print("   - GET  /messages/unanalyzed      (AI 미분석 메시지)")
    print("   - PUT  /messages/{id}/ai-analysis (AI 분석 결과 저장)")
    print("   - GET  /messages/historical      (과거 데이터 조회)")
    print("   - GET  /stats/processing         (처리 현황 통계)")

    uvicorn.run(app, host="0.0.0.0", port=8000)
