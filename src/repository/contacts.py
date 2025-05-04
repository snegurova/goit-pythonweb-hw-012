"""Contact repository for managing contact-related database operations.

This module provides methods to create, read, update, and delete contacts,
as well as to retrieve contacts with upcoming birthdays.

It uses SQLAlchemy for database interactions and is designed to work with 
an asynchronous FastAPI application.
"""
from typing import List
from datetime import date, timedelta

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate

class ContactRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize the ContactRepository with a database session.

        Args:
            session (AsyncSession): The database session to use for queries.
        """
        self.db = session

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        first_name: str | None,
        last_name: str | None,
        email: str | None,
        user: User
    ) -> List[Contact]:
        """
        Get a list of contacts for a specific user with optional filters.

        Args:
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to return.
            first_name (str | None): Filter by first name.
            last_name (str | None): Filter by last name.
            email (str | None): Filter by email.
            user (User): The user whose contacts are being retrieved.

        Returns:
            List[Contact]: A list of contacts matching the criteria.
        """
        stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)

        if first_name:
            stmt = stmt.where(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.where(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            stmt = stmt.where(Contact.email.ilike(f"%{email}%"))

        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Get a contact by its ID for a specific user.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user whose contact is being retrieved.

        Returns:
            Contact | None: The contact if found, otherwise None.
        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactCreate, user: User) -> Contact:
        """
        Create a new contact for a specific user.

        Args:
            body (ContactCreate): The contact data to create.
            user (User): The user for whom the contact is being created.

        Returns:
            Contact: The created contact.
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user=user)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact_by_id(contact.id, user)

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Remove a contact by its ID for a specific user.

        Args:
            contact_id (int): The ID of the contact to remove.
            user (User): The user whose contact is being removed.

        Returns:
            Contact | None: The removed contact if found, otherwise None.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate, user: User) -> Contact | None:
        """
        Update a contact by its ID for a specific user.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactUpdate): The updated contact data.
            user (User): The user whose contact is being updated.

        Returns:
            Contact | None: The updated contact if found, otherwise None.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def get_upcoming_birthdays(
        self,
        skip: int,
        limit: int,
        user: User,
    ) -> List[Contact]:
        """
        Get a list of contacts with upcoming birthdays for a specific user.

        Args:
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to return.
            user (User): The user whose contacts are being retrieved.
        
        Returns:
            List[Contact]: A list of contacts with upcoming birthdays.
        """
        today = date.today()
        next_week = today + timedelta(days=7)

        today_str = today.strftime("%m-%d")
        next_week_str = next_week.strftime("%m-%d")

        date_expr = func.to_char(Contact.birthday, 'MM-DD')

        stmt = (
            select(Contact)
            .filter_by(user=user)
            .where(
                or_(
                    date_expr.between(today_str, '12-31'),
                    date_expr.between('01-01', next_week_str)
                )
            )
            .offset(skip)
            .limit(limit)
        )

        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
