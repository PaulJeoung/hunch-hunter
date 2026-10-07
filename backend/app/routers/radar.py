import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Query
from supabase import create_client, Client
from app.core.security import get_current_user, CurrentUser

load_dotenv()

router = APIRouter(prefix="/api/radar", tags=["Radar"])

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
# supabase: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get("/signals")
def get_signals(
    date: Optional[str] = Query(None),
    user: CurrentUser = Depends(get_current_user)
):
    if not supabase:
        return {"tier": user.role, "is_truncated": False, "total_count": 0, "data": []}

    query = supabase.table("accumulation_signals").select("*, stocks(name)")
    if date:
        query = query.eq("signal_date", date)
    else:
        latest = supabase.table("accumulation_signals").select("signal_date").order("signal_date", desc=True).limit(1).execute()
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