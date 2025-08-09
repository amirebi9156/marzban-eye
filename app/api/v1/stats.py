# app/api/v1/stats.py
from fastapi import APIRouter, Depends, Query
from app.core.auth import get_current_user
from app.services.marzban_client import marzban
import os
import datetime
from datetime import datetime as dt
from datetime import timezone

router = APIRouter(prefix="/stats", tags=["stats"])

# آستانه آنلاین از ENV (دقیقه)
ONLINE_THRESHOLD_MIN = int(os.getenv("ONLINE_THRESHOLD_MIN", "5"))

def format_bytes(size):
    """تبدیل بایت به نمایش خوانا (B/KB/MB/GB/…)"""
    if size is None:
        return None
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    s = float(size)
    for unit in units:
        if s < 1024.0:
            return f"{s:.2f} {unit}"
        s /= 1024.0
    return f"{s:.2f} PB"

def format_timedelta(delta: datetime.timedelta):
    """نمایش روز و ساعت (بدون دقیقه) مثل: 2 روز و 5 ساعت"""
    if delta is None:
        return None
    days = delta.days
    hours = delta.seconds // 3600
    return f"{days} روز و {hours} ساعت"

def _parse_iso(iso_str: str):
    """ISO8601 -> datetime(UTC)"""
    if not iso_str:
        return None
    try:
        iso_str = iso_str.replace("Z", "+00:00")
        d = dt.fromisoformat(iso_str)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except Exception:
        return None

def _parse_any(ts):
    """
    ورودی ممکن است:
    - عدد/رشتهٔ عددی (UNIX seconds)
    - رشتهٔ ISO
    - None
    خروجی: datetime(UTC) یا None
    """
    if ts is None:
        return None
    # عددی/رشتهٔ عددی؟
    if isinstance(ts, (int, float)):
        try:
            return dt.fromtimestamp(float(ts), tz=timezone.utc)
        except Exception:
            return None
    if isinstance(ts, str):
        s = ts.strip()
        # اگر تماماً عدد بود → ثانیه
        if s.replace(".", "", 1).isdigit():
            try:
                return dt.fromtimestamp(float(s), tz=timezone.utc)
            except Exception:
                pass
        # در غیر این‌صورت ISO
        return _parse_iso(s)
    return None

def _to_human_delta_from_dt(d: dt):
    if not d:
        return None
    now = dt.now(timezone.utc)
    delta = now - d
    if delta.total_seconds() < 0:
        return None
    return format_timedelta(delta) + " پیش"

@router.get("/users/details", dependencies=[Depends(get_current_user)])
def user_details(limit: int = Query(50, ge=1, le=500)):
    """
    نمایش تمام جزئیات کاربردی کاربران
    """
    users = marzban.list_users().get("users", [])
    result = []

    now = dt.now(timezone.utc)
    threshold_sec = ONLINE_THRESHOLD_MIN * 60

    for user in users:
        username = user.get("username")

        used_raw = user.get("used_traffic", 0)               # برای سورت
        limit_raw = user.get("data_limit")                    # ممکن است None
        expire_ts = user.get("expire")                        # یونیکس ثانیه
        created_at = user.get("created_at")

        # این‌ها ممکن است ISO یا timestamp باشند
        online_at_raw = user.get("online_at")
        sub_updated_raw = user.get("sub_updated_at")

        last_online_dt = _parse_any(online_at_raw)
        last_sub_dt = _parse_any(sub_updated_raw)

        status = user.get("status")
        inbounds = user.get("inbounds", {})
        sub_last_agent = user.get("sub_last_user_agent")

        # درصد مصرف
        percent_used = (used_raw / limit_raw * 100) if limit_raw and limit_raw > 0 else None

        # تاریخ انقضا
        expire_date_str = "∞"
        expire_in_str = "∞"
        if expire_ts:
            expire_dt = dt.fromtimestamp(expire_ts, tz=timezone.utc)
            expire_date_str = expire_dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            delta = expire_dt - now
            expire_in_str = "منقضی شده" if delta.total_seconds() <= 0 else format_timedelta(delta)

        # انسانی از روی datetime
        last_online_str = _to_human_delta_from_dt(last_online_dt)
        last_sub_use_str = _to_human_delta_from_dt(last_sub_dt)

        # تشخیص آنلاینِ لحظه‌ای در بک‌اند
        online_now = False
        seconds_ago = None
        if last_online_dt:
            seconds_ago = int((now - last_online_dt).total_seconds())
            online_now = seconds_ago <= threshold_sec

        result.append({
            "username": username,
            "status": status,

            # نمایش‌های انسانی
            "used": format_bytes(used_raw),
            "limit": format_bytes(limit_raw) if limit_raw else None,
            "percent_used": f"{percent_used:.2f}%" if percent_used is not None else None,
            "expire_date": expire_date_str,
            "expire_in": expire_in_str,

            # خام/متادیتا
            "used_raw": used_raw,
            "limit_raw": limit_raw,
            "created_at": created_at,

            # زمان‌ها
            "last_online": last_online_str,                     # متن خوانا
            "last_online_iso": last_online_dt.isoformat() if last_online_dt else None,
            "last_online_seconds_ago": seconds_ago,

            "last_sub_update": last_sub_use_str,
            "last_sub_update_iso": last_sub_dt.isoformat() if last_sub_dt else None,
            "last_sub_update_raw": sub_updated_raw,

            # وضعیت آنلاین محاسبه‌شده در سرور
            "online_now": online_now,

            "last_user_agent": sub_last_agent,
            "inbounds": inbounds,
        })

    # مرتب‌سازی بر اساس مصرف واقعی
    result.sort(key=lambda x: x.get("used_raw") or 0, reverse=True)

    # برای هم‌راستاسازی فرانت
    return {
        "server_now_iso": now.isoformat(),
        "online_threshold_sec": threshold_sec,
        "users": result[:limit],
    }
