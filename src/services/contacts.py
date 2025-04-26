from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate, ContactUpdate
from src.database.models import User


def _handle_integrity_error(e: IntegrityError):
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
class ContactService:
    def __init__(self, db: AsyncSession):
        self.contact_repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreate, user: User):
        try:
            return await self.contact_repository.create_contact(body, user)
        except IntegrityError as e:
            await self.contact_repository.db.rollback()
            _handle_integrity_error(e)

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        first_name: str | None,
        last_name: str | None,
        email: str | None,
        user: User,
    ):
        return await self.contact_repository.get_contacts(skip, limit, first_name, last_name, email, user)

    async def get_contact(self, contact_id: int, user: User):
        return await self.contact_repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        try:
            return await self.contact_repository.update_contact(contact_id, body, user)
        except IntegrityError as e:
            await self.contact_repository.db.rollback()
            _handle_integrity_error(e)

    async def remove_contact(self, contact_id: int, user: User):
        return await self.contact_repository.remove_contact(contact_id, user)
    
    async def get_upcoming_birthdays(self, skip: int, limit: int, user: User):
        return await self.contact_repository.get_upcoming_birthdays(skip, limit, user)
