import os
from typing import Optional


class SupabaseClientPlaceholder:
    def __init__(self) -> None:
        self.url: Optional[str] = os.getenv("SUPABASE_URL")
        self.anon_key: Optional[str] = os.getenv("SUPABASE_ANON_KEY")

    @property
    def configured(self) -> bool:
        return bool(self.url and self.anon_key)


def get_supabase_client() -> SupabaseClientPlaceholder:
    return SupabaseClientPlaceholder()
