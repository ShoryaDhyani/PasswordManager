from urllib.parse import urlencode
from typing import Any, Dict, Optional

from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client.errors import MismatchingStateError
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from config import settings
from crypt import load_vault, save_vault

app = FastAPI(title="Password Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    https_only=settings.session_https_only,
    max_age=settings.session_max_age_seconds,
    same_site=settings.session_same_site,
    session_cookie=settings.session_cookie_name,
)

oauth = OAuth()

oauth.register(
    name="oidc",
    client_id=settings.cognito_client_id,
    client_secret=settings.cognito_client_secret,
    server_metadata_url=settings.cognito_metadata_url,
    client_kwargs={"scope": settings.cognito_scopes},
)


class VaultEntry(BaseModel):
    username: str
    password: str
    notes: Optional[str] = None


def _current_user(request: Request) -> Dict[str, Any]:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if "sub" not in user:
        raise HTTPException(status_code=400, detail="Invalid user session")
    return user


def _current_user_id(user: Dict[str, Any] = Depends(_current_user)) -> str:
    return user["sub"]


def _load_user_vault(user_id: str) -> Dict[str, Any]:
    try:
        vault, _ = load_vault(user_id)
        return vault
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Vault load failed") from exc


def _save_user_vault(user_id: str, vault: Dict[str, Any]) -> None:
    try:
        save_vault(user_id, vault)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Vault save failed") from exc


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user = request.session.get("user")
    if user:
        email = user.get("email", "user")
        return f'Hello, {email}. <a href="/logout">Logout</a>'
    return 'Welcome! Please <a href="/login">Login</a>.'


@app.get("/login")
async def login(request: Request):
    request.session.pop("user", None)
    return await oauth.oidc.authorize_redirect(request, settings.cognito_redirect_uri)


@app.get("/authorize")
async def authorize(request: Request):
    try:
        token = await oauth.oidc.authorize_access_token(request)
    except MismatchingStateError:
        request.session.clear()
        return RedirectResponse(url=settings.frontend_login_url)

    user = token.get("userinfo")
    if not user:
        user = await oauth.oidc.parse_id_token(request, token)
    request.session["user"] = dict(user)
    return RedirectResponse(url=settings.frontend_app_url)


@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    query = urlencode(
        {
            "client_id": settings.cognito_client_id,
            "logout_uri": settings.frontend_login_url,
        }
    )
    logout_url = f"https://{settings.cognito_domain}/logout?{query}"
    
    return RedirectResponse(url=logout_url)


@app.get("/api/me")
async def me(user: Dict[str, Any] = Depends(_current_user)):
    return {
        "sub": user.get("sub"),
        "email": user.get("email"),
    }


@app.get("/api/vault")
async def get_vault(user_id: str = Depends(_current_user_id)):
    vault = _load_user_vault(user_id)
    return {"vault": vault}


@app.get("/api/vault/{service}")
async def get_vault_entry(service: str, user_id: str = Depends(_current_user_id)):
    vault = _load_user_vault(user_id)
    if service not in vault:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"service": service, "entry": vault[service]}


@app.put("/api/vault/{service}")
async def put_vault_entry(
    service: str,
    entry: VaultEntry,
    user_id: str = Depends(_current_user_id),
):
    vault = _load_user_vault(user_id)
    vault[service] = entry.dict()
    _save_user_vault(user_id, vault)
    return {"service": service, "entry": vault[service]}


@app.delete("/api/vault/{service}")
async def delete_vault_entry(service: str, user_id: str = Depends(_current_user_id)):
    vault = _load_user_vault(user_id)
    if service not in vault:
        raise HTTPException(status_code=404, detail="Service not found")
    del vault[service]
    _save_user_vault(user_id, vault)
    return {"deleted": service}
