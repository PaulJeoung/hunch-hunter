# app/services/signal_service.py
from typing import Any, Dict, List
from app.core.database import get_supabase

def fetch_and_format_signals(table_name: str, date: str | None, user_role: str) -> Dict[str, Any]:
    client = get_supabase()
    if not client:
        return {"tier": user_role, "is_truncated": False, "total_count": 0, "data": []}

    query = client.table(table_name).select("*, stocks(name)")
    if date:
        query = query.eq("signal_date", date)
    else:
        latest = client.table(table_name).select("signal_date").order("signal_date", desc=True).limit(1).execute()
        if latest.data:
            query = query.eq("signal_date", latest.data[0]["signal_date"])

    res = query.order("score", desc=True).execute()
    data = res.data or []

    is_free = (user_role == "USER")
    return {
        "tier": "FREE" if is_free else user_role,
        "is_truncated": is_free,
        "total_count": len(data),
        "data": data[:3] if is_free else data
    }