from datetime import datetime
from bson.objectid import ObjectId

from fastapi import File, UploadFile
from api.model.base_model import PyObjectId
from pydantic import BaseModel, EmailStr, Field
import json

class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(..., max_length=50)
    password: str = Field(...)
    name: str = Field(..., max_length=100)
    email: EmailStr = Field(...)
    description: str = Field(None, max_length=255)
    uiIdentityNumber: str = Field(..., max_length=50)
    faculty: str = Field(..., max_length=50)
    classOf: str = Field(..., max_length=10)
    image: str = Field(None)
    linkedin: str = Field(None, max_length=100)
    twitter: str = Field(None, max_length=100)
    instagram: str = Field(None, max_length=100)
    tiktok: str = Field(None, max_length=100)
    communityEnrolled: list[str] = Field([])
    eventEnrolled: list[str] = Field([])
    joinedAt: datetime = Field(None)
    updatedAt: datetime = Field(None)

    class Config:
        json_encoders = {ObjectId: str}


class updateUser(BaseModel):
    name: str = Field(..., max_length=100)
    description: str = Field(None, max_length=255)
    faculty: str = Field(..., max_length=50)
    classOf: str = Field(..., max_length=10)
    image: str = Field(None)
    linkedin: str = Field(None, max_length=100)
    twitter: str = Field(None, max_length=100)
    instagram: str = Field(None, max_length=100)
    tiktok: str = Field(None, max_length=100)
    updatedAt: datetime = Field(...)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
        