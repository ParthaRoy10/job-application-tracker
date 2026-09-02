from datetime import datetime,date

from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime


class UserLogin(BaseModel):
    email: str
    password: str


class ApplicationCreate(BaseModel):
    company_id : int
    status: str
    date_applied:date


class ApplicationResponse(BaseModel):
    id : int
    user_id: int
    company_id : int
    status : str
    date_applied : date
    created_at: datetime
    updated_at : datetime

class ApplicationUpdate(BaseModel):
    status : str
