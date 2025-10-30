import os
from supabase import create_client, Client

# Workaround: gotrue uses 'proxy' arg unsupported by httpx>=0.24.
# Monkeypatch to ignore 'proxy' when constructing SyncClient.
_gotrue_patched = False

def _patch_gotrue_httpx_proxy():
    global _gotrue_patched
    if _gotrue_patched:
        return
    try:
        from gotrue._sync import gotrue_base_api as gb  # type: ignore
        from httpx import SyncClient as _HttpxSyncClient  # type: ignore

        # Replace the SyncClient reference in gotrue module with a factory
        # that ignores unsupported 'proxy' arg.
        def _sync_client_factory(*, verify: bool = True, proxy=None, follow_redirects: bool = True, http2: bool = True):
            return _HttpxSyncClient(
                verify=bool(verify),
                follow_redirects=follow_redirects,
                http2=http2,
            )

        gb.SyncClient = _sync_client_factory  # type: ignore
        _gotrue_patched = True
    except Exception:
        # If patch fails, proceed; errors will surface during client creation
        pass

_anon_client: Client | None = None
_service_client: Client | None = None

def get_anon_client() -> Client:
    global _anon_client
    if _anon_client is not None:
        return _anon_client
    _patch_gotrue_httpx_proxy()
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY")
    if not supabase_url or not supabase_anon_key:
        raise RuntimeError("SUPABASE_URL e SUPABASE_ANON_KEY são obrigatórios no .env")
    _anon_client = create_client(supabase_url, supabase_anon_key)
    return _anon_client

def get_service_client() -> Client | None:
    global _service_client
    if _service_client is not None:
        return _service_client
    _patch_gotrue_httpx_proxy()
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not supabase_service_key:
        _service_client = None
        return _service_client
    _service_client = create_client(supabase_url, supabase_service_key)
    return _service_client