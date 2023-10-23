from typing import Optional
from uuid import uuid4
from datetime import datetime

from fastapi import FastAPI, UploadFile

from pydantic import BaseModel, EmailStr, Field
from api.service.PH_Main import user as user_service
from api.model.PH_Main import user
from ..base_model import PyObjectId
from bson.objectid import ObjectId
from datetime import datetime, timezone
from pydantic.datetime_parse import parse_datetime
from fastapi import Security
import pytz

class utc_datetime(datetime):
    @classmethod
    def __get_validators__(cls):
        yield parse_datetime  # default pydantic behavior
        yield cls.ensure_tzinfo

    @classmethod
    def ensure_tzinfo(cls, v):
        # if TZ isn't provided, we assume UTC, but you can do w/e you need
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        # else we convert to utc
        return v.astimezone(timezone.utc)

    @staticmethod
    def to_str(dt: datetime) -> str:
        return dt.isoformat()  # replace with w/e format you want

class CommentModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(None)
    content: str = Field(..., max_length = 100)
    link: str = Field(None, max_length = 255)
    email: EmailStr = Field(None) 
    postId: str = Field(None)
    userLiked: list[EmailStr] = Field(None)
    createdAt: datetime = Field(default=datetime.now().astimezone(pytz.timezone('Asia/Jakarta')).isoformat(timespec='seconds'))
    updatedAt: datetime = Field(default=datetime.now().astimezone(pytz.timezone('Asia/Jakarta')).isoformat(timespec='seconds'))

    

    class Config:
        json_encoders = {
            ObjectId: str
        }
    

class UpdateCommentModel(BaseModel):
    content: Optional[str]
    updatedAt: datetime = Field(default=datetime.now().astimezone(pytz.timezone('Asia/Jakarta')).isoformat(timespec='seconds'))