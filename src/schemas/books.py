from pydantic import BaseModel, ConfigDict, Field


class NewBookChema(BaseModel):
    title: str = Field(max_length=50)
    author: str = Field(max_length=100)

    model_config = ConfigDict(extra='forbid')