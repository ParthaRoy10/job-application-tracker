from datetime import datetime,date

from enum import Enum
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


class ApplicationStatus(str, Enum):
    APPLIED = "APPLIED"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    SELECTED = "SELECTED"
class ApplicationCreate(BaseModel):
    company_id : int
    status: ApplicationStatus
    date_applied:date


class ApplicationResponse(BaseModel):
    id : int
    user_id: int
    company_id : int
    status : ApplicationStatus
    date_applied : date
    created_at: datetime
    updated_at : datetime

class ApplicationUpdate(BaseModel):
    status : ApplicationStatus


class CompanyCreate(BaseModel):
    company_name: str
    position: str
    ctc : float 
    location : str
    date_visiting : date




class CompanyResponse(BaseModel):
    id : int
    company_name: str
    position : str
    ctc : float
    location : str
    date_visiting : date
    created_at : datetime



