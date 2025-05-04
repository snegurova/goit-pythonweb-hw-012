"""
Service layer for managing contact operations.

This module contains the ContactService class, which coordinates business logic
and handles error management for contact-related functionality, including creation,
retrieval, update, deletion, and birthday queries.
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from functools import wraps

from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate, ContactUpdate
from src.database.models import User

def _handle_integrity_error(e: IntegrityError):
    """
    Raise appropriate HTTPException based on the type of IntegrityError.

    Args:
        e (IntegrityError): The caught SQLAlchemy IntegrityError exception.

    Raises:
        HTTPException: 409 if duplicate email, 400 for other integrity issues.
    """
    if "uq_user_email" in str(e.orig):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The contact with this email already exists.",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The integrity error occurred.",
        )

def handle_integrity_error(func):
    """
    Decorator to catch and handle SQLAlchemy IntegrityErrors in service methods.

    Rolls back the transaction if the repository has a database session.

    Args:
        func (Callable): The async function to wrap.

    Returns:
        Callable: The wrapped async function with error handling.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            self_instance = args[0]
            if hasattr(self_instance, 'contact_repository'):
                repo = getattr(self_instance, 'contact_repository')
                if hasattr(repo, 'db'):
                    await repo.db.rollback()
            _handle_integrity_error(e)
    return wrapper
class ContactService:
    """
    Service class for performing operations on contacts.

    Provides methods to create, retrieve, update, and delete contacts,
    as well as to find contacts with upcoming birthdays.
    """
    def __init__(self, db: AsyncSession):
        """
        Initialize the ContactService with a database session.

        Args:
            db (AsyncSession): SQLAlchemy asynchronous database session.
        """
        self.contact_repository = ContactRepository(db)

    @handle_integrity_error
    async def create_contact(self, body: ContactCreate, user: User):
        """
        Create a new contact for the given user.

        Args:
            body (ContactCreate): The contact data to create.
            user (User): The user who owns the contact.

        Returns:
            Contact: The created contact object.
        """
        return await self.contact_repository.create_contact(body, user)

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        first_name: str | None,
        last_name: str | None,
        email: str | None,
        user: User,
    ):
        """
        Retrieve contacts for a user, optionally filtered by name or email.

        Args:
            skip (int): Number of records to skip.
            limit (int): Max number of records to return.
            first_name (str | None): Optional filter by first name.
            last_name (str | None): Optional filter by last name.
            email (str | None): Optional filter by email.
            user (User): The user whose contacts to retrieve.

        Returns:
            List[Contact]: A list of contact objects.
        """
        return await self.contact_repository.get_contacts(skip, limit, first_name, last_name, email, user)

    async def get_contact(self, contact_id: int, user: User):
        """
        Retrieve a contact by its ID.

        Args:
            contact_id (int): The ID of the contact.
            user (User): The owner of the contact.

        Returns:
            Contact | None: The contact if found, otherwise None.
        """
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    @handle_integrity_error
    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        """
        Update an existing contact for the user.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactUpdate): The updated contact data.
            user (User): The owner of the contact.

        Returns:
            Contact: The updated contact object.
        """
        return await self.contact_repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Delete a contact by its ID.

        Args:
            contact_id (int): The ID of the contact to delete.
            user (User): The owner of the contact.

        Returns:
            Contact: The deleted contact object.
        """
        return await self.contact_repository.remove_contact(contact_id, user)
    
    async def get_upcoming_birthdays(self, skip: int, limit: int, user: User):
        """
        Retrieve contacts with birthdays within next week.

        Args:
            skip (int): Number of records to skip.
            limit (int): Max number of records to return.
            user (User): The owner of the contacts.

        Returns:
            List[Contact]: A list of upcoming birthday contacts.
        """
        return await self.contact_repository.get_upcoming_birthdays(skip, limit, user)
