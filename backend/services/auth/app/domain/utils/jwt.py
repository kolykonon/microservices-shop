import datetime
from typing import Any

import jwt
from app.infra.config import settings
from jwt.exceptions import InvalidTokenError


def _form_jwt_payload(
    payload: dict[str, Any],
    token_type: str,
) -> dict[str, Any]:
    payload["iat"] = datetime.datetime.now(datetime.UTC)
    payload["iss"] = "auth-service"
    payload["aud"] = "shop"
    if token_type == settings.jwt_access_token_type:
        payload.update(
            exp=datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(minutes=settings.jwt_access_token_expire_minutes),
            token_type=settings.jwt_access_token_type,
        )
    elif token_type == settings.jwt_refresh_token_type:
        payload.update(
            exp=datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(days=settings.jwt_refresh_token_expire_days),
            token_type=settings.jwt_refresh_token_type,
        )
    else:
        raise InvalidTokenError("Unknown token type")
    return payload


def encode_token(
    payload: dict[str, Any],
    token_type: str,
) -> str:
    payload = _form_jwt_payload(payload, token_type)
    return jwt.encode(
        payload=payload,
        key=settings.jwt_private_key_path.read_text(),
        algorithm=settings.jwt_encode_algorithm,
    )


def decode_token(
    token: str,
) -> dict:
    return jwt.decode(
        jwt=token,
        key=settings.jwt_public_key_path.read_text(),
        algorithms=[settings.jwt_encode_algorithm],
    )
