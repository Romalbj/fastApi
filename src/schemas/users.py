import re

from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr


class UserBase(BaseModel):
    username: str = Field(min_length=5, max_length=30)
    email: EmailStr = Field(min_length=10, max_length=30)


class CreateUserRequest(UserBase):
    password: str = Field(min_length=10, max_length=30)
    # password_repeat: str = Field(min_length=10, max_length=20)

    model_config = ConfigDict(from_attributes=True)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        #  1. Хотя бы одна цифра
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру.")

        # 2. Хотя бы одна заглавная буква
        if not re.search(r"[A-Z]", v):
            
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву.")

        # 3. Хотя бы одна строчная буква
        if not re.search(r"[a-z]", v):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву.")

        # 4. Хотя бы один спецсимвол (не буква и не цифра). 
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Пароль должен содержать хотя бы один спецсимвол.")

        return v     


class UserForPost(UserBase):
    id: int 

        
        


class Token(BaseModel):
    access_token: str
    token_type: str