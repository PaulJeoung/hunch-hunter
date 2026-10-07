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
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class CurrentUser(BaseModel):
    id: str
    email: str
    role: str = "USER"

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

        # 🔹 DB의 user_profiles 테이블에서 실제 role 조회
        role = "USER"
        if user_id:
            profile_res = supabase.table("user_profiles").select("role").eq("id", user_id).execute()
            if profile_res.data and len(profile_res.data) > 0:
                role = profile_res.data[0].get("role", "USER")

        return CurrentUser(id=user_id, email=email, role=role)
    except Exception as e:
        print(f"[Security Warning] 토큰 디코딩 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"유효하지 않은 토큰입니다: {str(e)}"
        )