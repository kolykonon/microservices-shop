from datetime import datetime, timedelta

import pytest
from jwt.exceptions import InvalidTokenError

from app.domain.utils.jwt import _calculate_lifetime, _form_jwt_payload, encode_token
from app.infra.config import settings


@pytest.fixture(scope="module")
def payload():
    return {"sub": 15}


def test_calculate_lifetime():
    assert _calculate_lifetime(settings.jwt_access_token_type) == timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    assert _calculate_lifetime(settings.jwt_refresh_token_type) == timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    with pytest.raises(InvalidTokenError):
        _calculate_lifetime("invalid_token_type")


def test_form_jwt_payload(payload):
    formed_payload = _form_jwt_payload(payload, settings.jwt_access_token_type)
    assert isinstance(formed_payload["iat"], datetime) == True
    assert isinstance(formed_payload["exp"], datetime) == True
    assert formed_payload["exp"] > formed_payload["iat"]
    assert formed_payload["iss"] == "auth-service"
    assert formed_payload["aud"] == "shop"
    assert isinstance(formed_payload["jti"], str) == True
    assert formed_payload["token_type"] == settings.jwt_access_token_type


def test_encode_token(payload):
    access_token = encode_token(payload, settings.jwt_access_token_type)
    assert isinstance(access_token.jti, str) == True
    assert isinstance(access_token.token, str) == True
    assert isinstance(access_token.expires_at, int) == True
