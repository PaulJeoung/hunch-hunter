import os
from typing import Optional
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase import create_client, Client

load_dotenv()

security = HTTPBearer(auto_error=False)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
supabase: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None

class CurrentUser(BaseModel):
    id: str
    email: str
    role: str = "USER"
    subscription_status: str = "FREE"

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> CurrentUser:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요한 서비스입니다."
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            options={"verify_signature": False, "verify_aud": False}
        )
        user_id = payload.get("sub", "")
        email = payload.get("email", "")

        role = "USER"
        status_val = "FREE"

        if supabase and user_id:
            try:
                res = (
                    supabase.table("user_profiles")
                    .select("role, subscription_status")
                    .eq("id", user_id)
                    .limit(1)
                    .execute()
                )
                if res.data and len(res.data) > 0:
                    profile = res.data[0]
                    role = profile.get("role", "USER")
                    status_val = profile.get("subscription_status", "FREE")
            except Exception as db_err:
                print(f"[Security Warning] DB 프로필 조회 실패: {db_err}")

        return CurrentUser(
            id=user_id,
            email=email,
            role=role,
            subscription_status=status_val
        )
    except Exception as e:
        print(f"[Security Warning] 토큰 디코딩 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"유효하지 않은 토큰입니다: {str(e)}"
        )