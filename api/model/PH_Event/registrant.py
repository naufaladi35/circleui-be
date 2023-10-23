from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field
from ..base_model import PyObjectId
from bson.objectid import ObjectId

class Registrant(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: EmailStr = Field(...)
    eventId: str = Field(...)
    joinedAt: datetime = Field(...)

    class Config:
          json_encoders = { ObjectId: str }