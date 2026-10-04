from datetime import datetime

from pydantic import BaseModel


class PayloadInfo(BaseModel):
    sub: str
    iat: datetime
    exp: datetime
    token_type: str
