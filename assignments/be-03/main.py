"""Per-request Supabase Auth integration for the Login & Protect assignment."""
import os
import httpx
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field
from supabase import create_client
from supabase_auth.errors import AuthApiError

app = FastAPI(title="Login & Protect")
bearer = HTTPBearer(auto_error=False)


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Invalid request"})


def auth_client():
    url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise HTTPException(503, "Supabase is not configured")
    # Do not share a mutable Supabase session between concurrent users.
    return create_client(url, key).auth


class Credentials(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    email: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=1, max_length=1024)


def verified_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Access token required")
    try:
        result = auth_client().get_user(credentials.credentials)
        if result is None or result.user is None:
            raise HTTPException(401, "Invalid or expired token")
        return result.user, credentials.credentials
    except AuthApiError as exc:
        if exc.status in (400, 401, 403):
            raise HTTPException(401, "Invalid or expired token") from exc
        raise HTTPException(503, "Authentication service unavailable") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(503, "Authentication service unavailable") from exc


@app.post("/auth/signup", status_code=201)
def signup(body: Credentials):
    try:
        result = auth_client().sign_up({"email": body.email, "password": body.password})
        return {"user": result.user.model_dump(mode="json") if result.user else None}
    except AuthApiError as exc:
        if exc.status in (400, 422):
            raise HTTPException(400, "Sign-up rejected") from exc
        raise HTTPException(503, "Authentication service unavailable") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(503, "Authentication service unavailable") from exc


@app.post("/auth/login")
def login(body: Credentials):
    try:
        result = auth_client().sign_in_with_password({"email": body.email, "password": body.password})
        if result.session is None:
            raise HTTPException(401, "Invalid login credentials")
        return {"access_token": result.session.access_token, "refresh_token": result.session.refresh_token}
    except AuthApiError as exc:
        if exc.status in (400, 401, 403):
            raise HTTPException(401, "Invalid login credentials") from exc
        raise HTTPException(503, "Authentication service unavailable") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(503, "Authentication service unavailable") from exc


@app.post("/auth/logout", status_code=204)
def logout(identity: Annotated[tuple, Depends(verified_user)]):
    try:
        auth_client().admin.sign_out(identity[1], scope="local")
    except (AuthApiError, httpx.HTTPError) as exc:
        raise HTTPException(503, "Could not revoke session") from exc
    return Response(status_code=204)


@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile")
def profile(identity: Annotated[tuple, Depends(verified_user)]):
    user = identity[0]
    return {"id": str(user.id), "email": user.email, "created_at": user.created_at}


@app.get("/protected/dashboard")
def dashboard(identity: Annotated[tuple, Depends(verified_user)]):
    return {"message": "Authenticated", "user_id": str(identity[0].id)}
