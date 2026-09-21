from supabase import Client, create_client

from app.core.config import settings

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)
