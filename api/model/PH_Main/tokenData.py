from pydantic import BaseModel, Field

class TokenData(BaseModel):
    username: str = Field(None)
    scopes: list[str] = Field(None)
    