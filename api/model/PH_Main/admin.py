from uuid import uuid4
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field

class Admin(BaseModel):
  id: uuid4
  name: str = Field(..., max_length = 100)
  email: EmailStr = Field(..., max_length = 50)
  joinedAt: datetime = Field(...)