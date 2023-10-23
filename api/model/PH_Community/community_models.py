from enum import Enum
from uuid import uuid4
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from bson.objectid import ObjectId
from typing import Optional, List
from ..base_model import PyObjectId
from datetime import datetime, timezone
import json
from pydantic.datetime_parse import parse_datetime
import pytz

class Status(str, Enum):
    open = 'open'
    closed = 'closed'
    not_active = 'not active'


class ManageMemberOption(str, Enum):
    approve = 'approve'
    reject = 'reject'
    remove = 'remove'


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


class CommunityModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., max_length=50)
    admin: EmailStr = Field(...)
    image: str = Field(None)
    shortDescription: str = Field(..., max_length=100)
    longDescription: str = Field(..., max_length=255)
    status: Status = Field(...)
    rules: str = Field(None, max_length=300)
    publicMembers: set[EmailStr] = Field([])
    pendingMembers: set[EmailStr] = Field([])
    totalMembers: int = Field(1)
    tags: set[str] = Field(None, max_length=20)
    createdAt: datetime = Field(default=datetime.now().astimezone(pytz.timezone('Asia/Jakarta')).isoformat(timespec='seconds'))
    updatedAt: datetime = Field(default=datetime.now().astimezone(pytz.timezone('Asia/Jakarta')).isoformat(timespec='seconds'))

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
        
    class Config:
        json_encoders = {
            ObjectId: str
        }


class UpdateCommunityModel(BaseModel):
    image: Optional[str]
    shortDescription: Optional[str]
    longDescription: Optional[str]
    status: Optional[Status]
    rules: Optional[str]
    publicMembers: Optional[set[EmailStr]]
    pendingMembers: Optional[set[EmailStr]]
    totalMembers: Optional[int]
    tags: Optional[set[str]]
    updatedAt: datetime = Field(default=datetime.now().astimezone(pytz.timezone('Asia/Jakarta')).isoformat(timespec='seconds'))
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class ManageMemberModel(BaseModel):
    email: EmailStr
    option: ManageMemberOption
