import os
from typing import Optional
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase: Optional[Client] = (
    create_client(SUPABASE_URL, SUPABASE_KEY) 
    if (SUPABASE_URL and SUPABASE_KEY) 
    else None
)

def get_supabase() -> Optional[Client]:
    return supabase