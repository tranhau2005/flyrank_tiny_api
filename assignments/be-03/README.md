# BE-03: Login & Protect

A FastAPI API using Supabase Auth. A new Supabase client is constructed per request so user sessions are not shared across callers. Set `SUPABASE_URL` and `SUPABASE_KEY` (a publishable/anon key) through your secret manager. Never commit keys.

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --port 8000
```

| Endpoint | Authentication | Success |
| --- | --- | --- |
| `POST /auth/signup` | No | 201 |
| `POST /auth/login` | No | 200 + tokens |
| `POST /auth/logout` | Bearer | 204 |
| `GET /public/info` | No | 200 |
| `GET /protected/profile` | Bearer | 200 |
| `GET /protected/dashboard` | Bearer | 200 |

Use `/docs` to sign up, sign in, and authorize with the access token. Supabase may require email confirmation before login. Logout revokes the refresh session; already-issued JWTs may remain valid until expiry, as described in [Supabase's sign-out documentation](https://supabase.com/docs/reference/python/auth-signout). Do not claim instant access-token revocation.

A live check with an existing test user verified login, the protected profile and dashboard, logout, and rejection of the revoked refresh token. It also checked that an unauthenticated profile request returns 401. Live sign-up and a Swagger screenshot remain unverified. This repo documents environment variable names instead of committing a dotenv file, as required by the workspace rules.

To repeat the live session check, supply `SUPABASE_URL`, `SUPABASE_KEY`, `TEST_EMAIL`, and `TEST_PASSWORD` through a secret manager and run `python tests/live_user_session.py`. Use only a dedicated test user: the test signs in and revokes the resulting refresh session. It intentionally does not print credentials, tokens, or profile details.
