from enum import Enum
from datetime import datetime
from bson.objectid import ObjectId

from fastapi import UploadFile
from pydantic import BaseModel, Field
from ..base_model import PyObjectId

class AnnouncementType(str, Enum):
  public = 'public'
  exclusive = 'exclusive'

class Announcement(BaseModel):
  id: PyObjectId = Field(default_factory = PyObjectId, alias="_id")
  content: str = Field(..., max_length = 255)
  link: str = Field(None, max_length = 255)
  attachment: UploadFile = Field(None)
  type: AnnouncementType = Field(...)
  communityId: str = Field(...)
  createdAt: datetime = Field(...)
  updatedAt: datetime = Field(...)

  class Config:
    json_encoders = {ObjectId: str}