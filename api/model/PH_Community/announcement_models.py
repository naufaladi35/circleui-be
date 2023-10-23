from enum import Enum
from datetime import datetime
from bson.objectid import ObjectId
from typing import Optional
from fastapi import UploadFile
from pydantic import BaseModel, Field
from ..base_model import PyObjectId
from datetime import datetime, timezone
from pydantic.datetime_parse import parse_datetime
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

class AnnouncementModel(BaseModel):
  id: PyObjectId = Field(default_factory = PyObjectId, alias="_id")
  content: str = Field(..., max_length = 255)
  link: str = Field(None, max_length = 255)
  # TODO: implement for uploading image
  communityId: str = Field(None)
  createdAt: datetime = Field(default=datetime.now().astimezone(pytz.timezone('Asia/Jakarta')).isoformat(timespec='seconds'))
  updatedAt: datetime = Field(default=datetime.now().astimezone(pytz.timezone('Asia/Jakarta')).isoformat(timespec='seconds'))

  class Config:
    json_encoders = {ObjectId: str}

class UpdateAnnouncementModel(BaseModel):
    content: Optional[str]
    updatedAt: datetime = Field(default=datetime.now().astimezone(pytz.timezone('Asia/Jakarta')).isoformat(timespec='seconds'))