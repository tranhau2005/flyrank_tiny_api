#!/usr/bin/env python3
"""Exercise the test user's session without printing credentials or tokens."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from supabase import create_client
from supabase_auth.errors import AuthApiError
from main import app


def check():
    with TestClient(app) as client:
        assert client.get("/public/info").status_code == 200, "public endpoint failed"
        assert client.get("/protected/profile").status_code == 401, "missing token was not rejected"
        login = client.post("/auth/login", json={"email": os.environ["TEST_EMAIL"], "password": os.environ["TEST_PASSWORD"]})
        assert login.status_code == 200, f"login failed, HTTP {login.status_code}"
        tokens = login.json()
        headers = {"Authorization": "Bearer " + tokens["access_token"]}
        profile = client.get("/protected/profile", headers=headers)
        assert profile.status_code == 200, f"profile failed, HTTP {profile.status_code}"
        assert profile.json()["email"].casefold() == os.environ["TEST_EMAIL"].casefold(), "wrong user"
        assert client.get("/protected/dashboard", headers=headers).status_code == 200, "dashboard failed"
        logout = client.post("/auth/logout", headers=headers)
        assert logout.status_code == 204, f"logout failed, HTTP {logout.status_code}"
        try:
            create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"]).auth.refresh_session(tokens["refresh_token"])
        except AuthApiError as exc:
            assert exc.status in (400, 401, 403), f"unexpected refresh rejection status {exc.status}"
        else:
            raise AssertionError("refresh token was accepted after logout")
    print("PASS: login, protected endpoints, logout and refresh-token rejection")


try:
    check()
except Exception as exc:
    # Provider errors can contain personal information or tokens; report only type.
    print("FAIL:", type(exc).__name__)
    if isinstance(exc, AssertionError):
        print(str(exc))
    sys.exit(1)
