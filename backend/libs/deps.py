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
    ):
        self.public_key = public_key
        self.audience = audience
        self.issuer = issuer

    def current_user(
        self,
        creds: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    ) -> PayloadInfo:
        try:
            payload = jwt.decode(
                creds.credentials,
                self.public_key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
            )
            info = PayloadInfo(**payload)
            return info
        except jwt.PyJWTError as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
