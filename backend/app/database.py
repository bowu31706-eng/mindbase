from supabase import create_client, Client
from functools import lru_cache
from app.config import get_settings


@lru_cache
def get_supabase() -> Client:
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_key)


@lru_cache
def get_supabase_admin() -> Client:
    """Service role client — 用于绕过 RLS，仅在后端内部使用"""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_key)
