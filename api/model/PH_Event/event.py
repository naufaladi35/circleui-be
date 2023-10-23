from datetime import datetime
from enum import Enum
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel, EmailStr, Field
from ..base_model import PyObjectId
from bson.objectid import ObjectId
import json

class Status(str, Enum):
    open = 'open'
    closed = 'closed'
    not_active = 'not active'

class Event(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., max_length = 50)
    status: Status = Field(...)
    description: str = Field(None, max_length = 255)
    dateTime: datetime = Field(...)
    location: str = Field(None, max_length = 30)
    contact: str = Field(None, max_length = 50)
    link: str = Field(None, max_length = 100)
    image: str = Field(None)
    price: str = Field(None, max_length = 10)
    organizer: EmailStr = Field(None)
    numberOfBookmark: int = Field(0, ge = 0)
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