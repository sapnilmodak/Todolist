from supabase import create_client
import os

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_table(table_name: str):
    """Returns a Supabase table object for CRUD operations."""
    return supabase.table(table_name)
