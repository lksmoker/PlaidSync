from supabase_client import supabase
from datetime import datetime

def log_message(message, severity="INFO", endpoint=""):
    """Log messages to the Supabase logs table."""
    try:
        log_entry = {
            "message": message,
            "severity": severity,
            "endpoint": endpoint,
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table("logs").insert(log_entry).execute()
    except Exception as e:
        print(f"Failed to log message: {e}")