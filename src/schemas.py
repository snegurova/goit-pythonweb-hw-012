"""
Pydantic schemas for request and response models used in the application.

Includes schemas for contact creation and updates, user management, token responses, and email verification.
"""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr

class ContactCreate(BaseModel):
    """
    Schema for creating a new contact.

    Includes basic contact details such as name, email, phone number, birthday, and optional extra info.
    """
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone_number: str = Field(min_length=10, max_length=15)
    birthday: date
    extra_info: Optional[str] = None

class ContactUpdate(BaseModel):
    """
    Schema for updating an existing contact.

    All fields are optional to support partial updates.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    birthday: Optional[date] = None
    extra_info: Optional[str] = None

class ContactResponse(ContactCreate):
    """
    Schema for returning contact information including ID.

    Inherits from ContactCreate and includes the contact's database ID.
    """
    id: int

    model_config = ConfigDict(from_attributes=True)
class User(BaseModel):
    """
    Schema representing a user in responses.

    Contains user ID, username, email, and avatar URL.
    """
    id: int
    username: str
    email: str
    avatar: str

    model_config = ConfigDict(from_attributes=True)
class UserCreate(BaseModel):
    """
    Schema for user registration requests.

    Includes username, email, and password.
    """
    username: str
    email: str
    password: str
class Token(BaseModel):
    """
    Schema for JWT token response.

    Contains the access token and its type.
    """
    access_token: str
    token_type: str

class RequestEmail(BaseModel):
    """
    Schema for requesting email-based actions (e.g. confirmation/resend).

    Contains the user's email address.
    """
    email: EmailStr
