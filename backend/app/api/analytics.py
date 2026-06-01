"""
Analytics API — page view tracking + admin reporting
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.database import get_db
from app.models.page_view import PageView
from app.core.deps import get_current_admin
from pydantic import BaseModel

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


# ── Schema ────────────────────────────────────────────────────────────────────
class TrackPayload(BaseModel):
    page_url:    str
    page_title:  Optional[str] = None
    referrer:    Optional[str] = None
    device_type: Optional[str] = None   # mobile | desktop | tablet
    session_id:  Optional[str] = None
    user_id:     Optional[int] = None


# ── Track endpoint (public — no auth required) ────────────────────────────────
@router.post("/track")
async def track_page_view(payload: TrackPayload, db: Session = Depends(get_db)):
    """
    Called on every page load from analytics-tracker.js.
    Stores the visit without any PII (no IP address).
    Returns 200 immediately — frontend never waits on this.
    """
    view = PageView(
        page_url    = payload.page_url[:500],
        page_title  = (payload.page_title or "")[:255],
        referrer    = (payload.referrer or "")[:500] or None,
        device_type = payload.device_type,
        session_id  = payload.session_id,
        user_id     = payload.user_id,
    )
    db.add(view)
    db.commit()
    return {"ok": True}


# ── Admin reporting endpoints ─────────────────────────────────────────────────
def _now():
    return datetime.now(tz=timezone.utc)


@router.get("/dashboard")
def analytics_dashboard(
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Full analytics summary for the admin dashboard."""
    now   = _now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week  = today - timedelta(days=7)
    month = today - timedelta(days=30)

    def count_since(dt):
        return db.query(func.count(PageView.id)).filter(PageView.created_at >= dt).scalar() or 0

    def unique_sessions_since(dt):
        return db.query(func.count(func.distinct(PageView.session_id))).filter(
            PageView.created_at >= dt, PageView.session_id.isnot(None)
        ).scalar() or 0

    # ── Core counts ──
    views_today  = count_since(today)
    views_week   = count_since(week)
    views_month  = count_since(month)
    visits_today = unique_sessions_since(today)
    visits_week  = unique_sessions_since(week)
    visits_month = unique_sessions_since(month)

    # ── Top pages (last 30 days) ──
    top_pages_rows = db.execute(text("""
        SELECT page_url, page_title, COUNT(*) AS views
        FROM page_views
        WHERE created_at >= :since
        GROUP BY page_url, page_title
        ORDER BY views DESC
        LIMIT 10
    """), {"since": month}).fetchall()
    top_pages = [{"url": r[0], "title": r[1] or r[0], "views": r[2]} for r in top_pages_rows]

    # ── Traffic sources (last 30 days) ──
    source_rows = db.execute(text("""
        SELECT
          CASE
            WHEN referrer IS NULL OR referrer = '' THEN 'Direct'
            WHEN referrer ILIKE '%google%'         THEN 'Google'
            WHEN referrer ILIKE '%facebook%'       THEN 'Facebook'
            WHEN referrer ILIKE '%whatsapp%'       THEN 'WhatsApp'
            WHEN referrer ILIKE '%instagram%'      THEN 'Instagram'
            WHEN referrer ILIKE '%twitter%'
              OR referrer ILIKE '%x.com%'          THEN 'Twitter / X'
            WHEN referrer ILIKE '%pikcarz.co.za%'  THEN 'Internal'
            ELSE 'Other'
          END AS source,
          COUNT(*) AS views
        FROM page_views
        WHERE created_at >= :since
        GROUP BY source
        ORDER BY views DESC
    """), {"since": month}).fetchall()
    sources = [{"source": r[0], "views": r[1]} for r in source_rows]

    # ── Device breakdown (last 30 days) ──
    device_rows = db.execute(text("""
        SELECT COALESCE(device_type, 'unknown') AS device, COUNT(*) AS views
        FROM page_views
        WHERE created_at >= :since
        GROUP BY device
        ORDER BY views DESC
    """), {"since": month}).fetchall()
    devices = [{"device": r[0], "views": r[1]} for r in device_rows]

    # ── Hourly traffic today ──
    hourly_rows = db.execute(text("""
        SELECT EXTRACT(HOUR FROM created_at AT TIME ZONE 'Africa/Johannesburg') AS hour,
               COUNT(*) AS views
        FROM page_views
        WHERE created_at >= :today
        GROUP BY hour
        ORDER BY hour
    """), {"today": today}).fetchall()
    hourly = [{"hour": int(r[0]), "views": r[1]} for r in hourly_rows]

    # ── Daily trend (last 14 days) ──
    daily_rows = db.execute(text("""
        SELECT DATE(created_at AT TIME ZONE 'Africa/Johannesburg') AS day,
               COUNT(*) AS views,
               COUNT(DISTINCT session_id) AS visits
        FROM page_views
        WHERE created_at >= :since
        GROUP BY day
        ORDER BY day
    """), {"since": today - timedelta(days=14)}).fetchall()
    daily = [{"date": str(r[0]), "views": r[1], "visits": r[2]} for r in daily_rows]

    return {
        "totals": {
            "views_today":   views_today,
            "views_week":    views_week,
            "views_month":   views_month,
            "visits_today":  visits_today,
            "visits_week":   visits_week,
            "visits_month":  visits_month,
        },
        "top_pages": top_pages,
        "sources":   sources,
        "devices":   devices,
        "hourly":    hourly,
        "daily":     daily,
    }
