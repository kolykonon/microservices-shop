import logging
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

from libs.schemas.payload import PayloadInfo

bearer = HTTPBearer()

logger = logging.getLogger(__name__)


class Auth:
    def __init__(
        self,
        public_key: str,
        audience: str = "shop",
        issuer: str = "auth-service",
        access_token_type: str = "access",
        algorithm: str = "RS256",
    ):
        self.public_key = public_key
        self.audience = audience
        self.issuer = issuer
        self.access_token_type = access_token_type
        self.algorithm = algorithm

    def current_user(
        self,
        creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    ) -> PayloadInfo:
        try:
            payload = jwt.decode(
                creds.credentials,
                self.public_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
            )
            if payload.get("token_type") != self.access_token_type:
                raise jwt.InvalidTokenError("Not an access token")
            return PayloadInfo(**payload)
        except jwt.PyJWTError as e:
            logger.warning("JWT rejected: %s", e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
