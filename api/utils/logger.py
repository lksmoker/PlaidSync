from supabase_client import supabase
from datetime import datetime

def log_message(message, severity="INFO", service="Backend", route=None):
    """Logs a message to the database."""
    try:
        log_entry = {
            "message": message,
            "severity": severity,
            "service": service,
            "route": route,  # ✅ Added this to match function calls
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table("logs").insert(log_entry).execute()
    except Exception as e:
        print(f"Logging failed: {e}")  # Fallback to console logging