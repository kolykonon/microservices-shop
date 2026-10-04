from pydantic import BaseModel


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class IssuedToken(BaseModel):
    token: str
    jti: str
    expires_at: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str
