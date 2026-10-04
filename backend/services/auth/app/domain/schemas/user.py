from datetime import datetime

from pydantic import BaseModel, Field, ValidationError, field_validator


def validate_email(email: str) -> bool:
    return True


def validate_password(password: str) -> bool:
    return True


class UserCreate(BaseModel):
    email: str = Field(max_length=100)
    password: str = Field(min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not validate_email(v):
            raise ValidationError("Error while validating email")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not validate_password(v):
            raise ValidationError("Error while validating password")
        return v


class UserCreateDB(BaseModel):
    email: str
    hashed_password: str

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: str | None = Field(max_length=100)
    password: str | None = Field(min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not validate_email(v):
            raise ValidationError("Error while validating email")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not validate_password(v):
            raise ValidationError("Error while validating password")
        return v


class UserUpdateDB(BaseModel):
    email: str | None
    hashed_password: str | None

    class Config:
        from_attributes = True


class UserRead(BaseModel):
    email: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
