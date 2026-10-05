import datetime
import uuid
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError

from app.domain.schemas.token import IssuedToken
from app.infra.config import settings


def _calculate_lifetime(
    token_type: str,
) -> datetime.timedelta:
    if token_type == settings.jwt_access_token_type:
        return datetime.timedelta(minutes=settings.jwt_access_token_expire_minutes)
    elif token_type == settings.jwt_refresh_token_type:
        return datetime.timedelta(days=settings.jwt_refresh_token_expire_days)
    else:
        raise InvalidTokenError("Unknown token type")


def _form_jwt_payload(
    payload: dict[str, Any],
    token_type: str,
) -> dict[str, Any]:
    now = datetime.datetime.now(datetime.UTC)
    return {
        **payload,
        "iat": now,
        "exp": now + _calculate_lifetime(token_type),
        "iss": "auth-service",
        "aud": "shop",
        "jti": str(uuid.uuid4()),
        "token_type": token_type,
    }


def encode_token(
    payload: dict[str, Any],
    token_type: str,
) -> IssuedToken:
    token_data = _form_jwt_payload(payload, token_type)
    token = jwt.encode(
        payload=token_data,
        key=settings.jwt_private_key_path.read_text(),
        algorithm=settings.jwt_encode_algorithm,
    )
    return IssuedToken(
        token=token,
        jti=token_data["jti"],
        expires_at=int(token_data["exp"].timestamp()),
    )


def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    payload = jwt.decode(
        jwt=token,
        key=settings.jwt_public_key_path.read_text(),
        algorithms=[settings.jwt_encode_algorithm],
        audience="shop",
        issuer="auth-service",
        options={"require": ["exp", "iat", "sub", "jti"]},
    )
    if expected_type is not None and payload.get("token_type") != expected_type:
        raise InvalidTokenError("Unexpected token type")
    return payload
