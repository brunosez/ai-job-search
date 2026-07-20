"""Gestion de l'authentification OAuth2 pour l'API France Travail."""
import os
import json
import time
import requests
from pathlib import Path

TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=%2Fpartenaire"
SCOPE = "api_offresdemploiv2 o2dsoffre"
CACHE_FILE = Path(__file__).parent / ".ft_token_cache.json"


def _load_cache():
    if CACHE_FILE.exists():
        try:
            data = json.loads(CACHE_FILE.read_text())
            if data.get("expires_at", 0) > time.time() + 30:
                return data.get("access_token")
        except Exception:
            pass
    return None


def _save_cache(token, expires_in):
    CACHE_FILE.write_text(json.dumps({
        "access_token": token,
        "expires_at": time.time() + expires_in
    }))


def get_access_token():
    cached = _load_cache()
    if cached:
        return cached

    client_id = os.environ.get("FT_CLIENT_ID")
    client_secret = os.environ.get("FT_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError(
            "FT_CLIENT_ID et FT_CLIENT_SECRET doivent etre definis dans l'environnement (.env)"
        )

    scope = f"application_{client_id} api_offresdemploiv2 o2dsoffre"

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    resp = requests.post(TOKEN_URL, data=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    token = data["access_token"]
    expires_in = data.get("expires_in", 1500)
    _save_cache(token, expires_in)
    return token