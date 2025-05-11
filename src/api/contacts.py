import json
from typing import List

from src.cache.redis_client import redis_client
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.services.auth import get_current_user
from src.database.db import get_db
from src.schemas import ContactCreate, ContactResponse, ContactUpdate
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a list of contacts with optional filtering.

    Args:
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        first_name (str | None): Filter by first name.
        last_name (str | None): Filter by last name.
        email (str | None): Filter by email.
        db (AsyncSession): The database session.
        user (User): The currently authenticated user.

    Returns:
        List[ContactResponse]: A list of matching contact records.
    """
    key = f"user:{user.id}:contacts:{skip}:{limit}:{first_name}:{last_name}:{email}"
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, first_name, last_name, email, user)
    redis_client.set(
        key,
        json.dumps([ContactResponse.model_validate(c).model_dump() for c in contacts], default=str),
        ex=60 * 60,
    )
    return contacts

@router.get("/upcoming-birthdays", response_model=List[ContactResponse])
async def get_birthdays(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve contacts with upcoming birthdays.

    Args:
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        db (AsyncSession): The database session.
        user (User): The currently authenticated user.

    Returns:
        List[ContactResponse]: A list of upcoming birthday contacts.
    """
    key = f"user:{user.id}:upcoming_birthdays:{skip}:{limit}"
    cached = redis_client.get(key)

    if cached:
        return json.loads(cached)

    contact_service = ContactService(db)
    birthdays = await contact_service.get_upcoming_birthdays(skip, limit, user)

    redis_client.set(
        key,
        json.dumps([ContactResponse.model_validate(b).model_dump() for b in birthdays], default=str),
        ex=60 * 60,
    )
    return birthdays

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Retrieve a single contact by ID.

    Args:
        contact_id (int): ID of the contact.
        db (AsyncSession): The database session.
        user (User): The currently authenticated user.

    Returns:
        ContactResponse: The contact if found.

    Raises:
        HTTPException: If the contact is not found.
    """
    key = f"user:{user.id}:contact:{contact_id}"
    cached = redis_client.get(key)

    if cached:
        return json.loads(cached)

    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact is not found"
        )

    redis_client.set(
    key,
    json.dumps(ContactResponse.model_validate(contact).model_dump(), default=str),
    ex=60 * 60,
)
    return contact

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Create a new contact for the current user.

    Args:
        body (ContactCreate): Data required to create a contact.
        db (AsyncSession): The database session.
        user (User): The currently authenticated user.

    Returns:
        ContactResponse: The newly created contact.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactUpdate, contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    """
    Update an existing contact by ID.

    Args:
        body (ContactUpdate): Updated contact data.
        contact_id (int): ID of the contact to update.
        db (AsyncSession): The database session.
        user (User): The currently authenticated user.

    Returns:
        ContactResponse: The updated contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact is not found"
        )
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_note(contact_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Delete a contact by ID.

    Args:
        contact_id (int): ID of the contact to delete.
        db (AsyncSession): The database session.
        user (User): The currently authenticated user.

    Returns:
        ContactResponse: The deleted contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact is not found"
        )
    return contact
