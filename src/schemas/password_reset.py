from datetime import datetime
import re

from pydantic import BaseModel, Field, field_validator, EmailStr

def validate_strong_password(v: str) -> str:
    if not re.search(r"\d", v):
        raise ValueError("Пароль должен содержать хотя бы одну цифру.")
    if not re.search(r"[A-Z]", v):
        raise ValueError("Пароль должен содержать хотя бы одну заглавную букву.")
    if not re.search(r"[a-z]", v):
        raise ValueError("Пароль должен содержать хотя бы одну строчную букву.")
    if not re.search(r"[^A-Za-z0-9]", v):
        raise ValueError("Пароль должен содержать хотя бы один спецсимвол.")
    return v


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(min_length=10, max_length=30)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=10, max_length=20)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return validate_strong_password(v)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=10, max_length=30)


    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return validate_strong_password(v)         