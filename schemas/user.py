from datetime import datetime
from typing import Optional

from pydantic import EmailStr, validator

from schemas.base import BaseSchema


# User schemas
class UserBase(BaseSchema):
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')

        return value


class UserLogin(BaseSchema):
    email: EmailStr
    password: str


class UserUpdate(BaseSchema):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
