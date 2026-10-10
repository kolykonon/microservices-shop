from typing import Annotated

from fastapi import Depends

from app.infra.config import settings
from libs.deps import Auth
from libs.schemas.payload import PayloadInfo

public_key = settings.jwt_public_key_path.read_text()

auth = Auth(public_key=public_key)

CurrentUser = Annotated[PayloadInfo, Depends(auth.current_user)]
