"""Check Supabase connectivity and rejection of a deliberately invalid token."""
import os
import httpx
from supabase import create_client
from supabase_auth.errors import AuthApiError

url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_KEY']
r = httpx.get(url.rstrip('/') + '/auth/v1/settings', headers={'apikey': key}, timeout=15)
print('Supabase Auth settings HTTP status:', r.status_code)
r.raise_for_status()
try:
    create_client(url, key).auth.get_user('invalid-test-token')
    raise SystemExit('Invalid token was unexpectedly accepted')
except AuthApiError as exc:
    print('Invalid-token rejection status:', exc.status)
    if exc.status not in (400, 401, 403):
        raise SystemExit('Unexpected authentication response')
