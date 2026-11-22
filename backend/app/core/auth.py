"""Simple bearer token authentication for demo purposes."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .settings import settings

security = HTTPBearer(auto_error=False)

# Demo tokens mapped to synthetic user identities
DEMO_TOKENS: dict[str, dict] = {
    settings.DEMO_TOKEN: {
        "sub": "demo-user",
        "name": "Demo Operator",
        "role": "admin",
    },
    "sentinel-readonly-token": {
        "sub": "readonly-user",
        "name": "Read-Only Viewer",
        "role": "viewer",
    },
}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Validate the bearer token and return the user identity.

    If no token is provided, returns a default anonymous user so that
    unauthenticated requests still work in demo mode.
    """
    if credentials is None:
        return {"sub": "anonymous", "name": "Anonymous", "role": "viewer"}

    token = credentials.credentials
    user = DEMO_TOKENS.get(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return user
