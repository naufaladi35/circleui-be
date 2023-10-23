import json
from datetime import datetime
from bson.objectid import ObjectId

from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, Field

from api.model.base_model import PyObjectId

class Post(BaseModel):
    id: PyObjectId = Field(default_factory = PyObjectId, alias = "_id")
    title: str = Field(..., max_length = 50)
    content: str = Field(..., max_length = 255)
    link: str = Field(None, max_length = 255)
    attachment_url: str = Field(None)
    likesCounter: int = Field(0, ge = 0)
    username: str = Field(None)
    creator: EmailStr = Field(None)
    communityId: str = Field(...)
    isUpdated: bool = Field(False)
    userLiked: list[EmailStr] = Field(None)
    createdAt: datetime = Field(None)
    updatedAt: datetime = Field(None)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    class Config:
        json_encoders = { ObjectId: str }
        orm_mode = True