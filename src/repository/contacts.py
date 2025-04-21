from typing import List
from datetime import date, timedelta

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate

class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        first_name: str | None,
        last_name: str | None,
        email: str | None,
    ) -> List[Contact]:
        stmt = select(Contact).offset(skip).limit(limit)

        if first_name:
            stmt = stmt.where(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            stmt = stmt.where(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            stmt = stmt.where(Contact.email.ilike(f"%{email}%"))

        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactCreate) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True))
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact_by_id(contact.id)

    async def remove_contact(self, contact_id: int) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
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
    ) -> List[Contact]:
        today = date.today()
        next_week = today + timedelta(days=7)

        today_str = today.strftime("%m-%d")
        next_week_str = next_week.strftime("%m-%d")

        date_expr = func.to_char(Contact.birthday, 'MM-DD')

        stmt = (
            select(Contact)
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
