from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr

class ContactCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone_number: str = Field(min_length=10, max_length=15)
    birthday: date
    extra_info: Optional[str] = None

class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    birthday: Optional[date] = None
    extra_info: Optional[str] = None

class ContactResponse(ContactCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
class User(BaseModel):
    id: int
    username: str
    email: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
class Token(BaseModel):
    access_token: str
    token_type: str

class RequestEmail(BaseModel):
    email: EmailStr
