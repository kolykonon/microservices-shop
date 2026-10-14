import re
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
)

PASSWORD_RULES = (
    (re.compile(r"[a-z]"), "Password must contain a lowercase letter"),
    (re.compile(r"[A-Z]"), "Password must contain an uppercase letter"),
    (re.compile(r"\d"), "Password must contain a digit"),
    (re.compile(r"[^\w\s]"), "Password must contain a special character"),
)


def check_password(password: str) -> str:
    if any(ch.isspace() for ch in password):
        raise ValueError("Password must not contain whitespace")
    for pattern, message in PASSWORD_RULES:
        if not pattern.search(password):
            raise ValueError(message)
    return password


class UserCreate(BaseModel):
    email: EmailStr = Field(max_length=100)
    password: SecretStr = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: SecretStr) -> SecretStr:
        check_password(v.get_secret_value())
        return v


class UserCreateDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str
    hashed_password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        return None if v is None else check_password(v)


class UserUpdateDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str | None
    hashed_password: str | None


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str | None
    created_at: datetime
    updated_at: datetime
