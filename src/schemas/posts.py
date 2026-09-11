from datetime import datetime

from pydantic import BaseModel, Field, field_validator, EmailStr

from src.models.models import User
from src.schemas.users import CreateUserRequest

class PostValidate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class PaginatedPostResponse(BaseModel):
    posts: list[PostValidate]
    total: int
    skip: int
    limit: int
    has_more: bool

