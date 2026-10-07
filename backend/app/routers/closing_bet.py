import os
from typing import Optional
from fastapi import APIRouter, Depends, Query
from supabase import create_client, Client
from app.core.security import get_current_user, CurrentUser

router = APIRouter(prefix="/api/closing-bet", tags=["Closing Bet"])

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

@router.get("/signals")
def get_closing_bet_signals(
    date: Optional[str] = Query(None),
    user: CurrentUser = Depends(get_current_user)
):
    if not supabase:
        return {"tier": user.role, "is_truncated": False, "total_count": 0, "data": []}

    query = supabase.table("closing_bet_signals").select("*, stocks(name)")
    if date:
        query = query.eq("signal_date", date)
    else:
        latest = supabase.table("closing_bet_signals").select("signal_date").order("signal_date", desc=True).limit(1).execute()
        if latest.data:
            query = query.eq("signal_date", latest.data[0]["signal_date"])

    query = query.order("score", desc=True)
    res = query.execute()
    data = res.data or []

    if user.role == "USER":
        return {
            "tier": "FREE",
            "is_truncated": True,
            "total_count": len(data),
            "data": data[:3]
        }

    return {
        "tier": user.role,
        "is_truncated": False,
        "total_count": len(data),
        "data": data
    }