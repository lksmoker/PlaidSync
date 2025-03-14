import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials not found. Set in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Supabase connected successfully.")