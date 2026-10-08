import os
from typing import Optional
from fastapi import APIRouter, Depends, Query
from supabase import create_client, Client
from app.core.security import get_current_user, CurrentUser

router = APIRouter(prefix="/api/radar", tags=["Radar"])

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None

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

    # 1. PRO 가입자이지만 관리자 미승인(DEACTIVE) 대기 상태인 경우 -> 1종목만 제한 제공
    if user.role == "PRO" and user.subscription_status == "DEACTIVE":
        return {
            "tier": "PENDING",
            "is_truncated": True,
            "message": "현재 관리자 승인 대기 중입니다.",
            "total_count": len(data),
            "data": data[:1]
        }

    # 2. 일반 무료 유저 (USER) -> 3종목 제공
    if user.role == "USER":
        return {
            "tier": "FREE",
            "is_truncated": True,
            "message": "PRO 구독 시 전체 발굴 종목을 모두 열람하실 수 있습니다.",
            "total_count": len(data),
            "data": data[:3]
        }

    # 3. 승인된 PRO 또는 ADMIN -> 전체 종목 제공
    return {
        "tier": user.role,
        "is_truncated": False,
        "message": "",
        "total_count": len(data),
        "data": data
    }