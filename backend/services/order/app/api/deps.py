from typing import Annotated

from fastapi import Depends
from fastapi.security.http import HTTPAuthorizationCredentials

from app.infra.config import settings
from libs.deps import Auth, bearer
from libs.schemas.payload import PayloadInfo

auth = Auth(public_key=settings.jwt_public_key_path.read_text())

CurrentUser = Annotated[PayloadInfo, Depends(auth.current_user)]

Token = Annotated[HTTPAuthorizationCredentials, Depends(bearer)]
