from uuid import uuid4
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel, Field

class Comment(BaseModel):
  id: uuid4
  content: str = Field(..., max_length = 100)
  creator: str = Field(...)
  eventId: str = Field(...)
  createdAt: datetime = Field(...)
  updatedAt: datetime = Field(...)