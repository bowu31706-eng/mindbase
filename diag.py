import sys
sys.path.insert(0, "D:/求职全过程/MindBase/backend")

import os
os.chdir("D:/求职全过程/MindBase/backend")

# Load dotenv manually
from dotenv import load_dotenv
load_dotenv("D:/求职全过程/MindBase/backend/.env")

print("SUPABASE_URL:", os.environ.get("SUPABASE_URL", "NOT SET"))
print("SUPABASE_KEY:", os.environ.get("SUPABASE_KEY", "NOT SET")[:30] + "...")
print("SUPABASE_SERVICE_KEY:", os.environ.get("SUPABASE_SERVICE_KEY", "NOT SET")[:30] + "...")

try:
    from supabase import create_client
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    print("\nCreating supabase client...")
    db = create_client(url, key)
    print("Client created OK")

    print("Querying users table...")
    result = db.table("users").select("id").limit(1).execute()
    print("Query result:", result.data)
    print("\nSupabase connection: OK")
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
