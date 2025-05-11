import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate, ContactUpdate
from src.database.models import Contact, User

@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)

@pytest.fixture
def test_user():
    return User(id=1, username="testuser", email="test@example.com")

@pytest.mark.asyncio
async def test_get_contacts_with_filter(contact_repository, mock_session, test_user):
    contact = Contact(
        id=1,
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        phone_number="+1234567890",
        birthday=date(1990, 5, 5),
        user=test_user
    )
    result_proxy = MagicMock()
    result_proxy.scalars().all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=result_proxy)

    contacts = await contact_repository.get_contacts(0, 10, "Alice", None, None, test_user)

    mock_session.execute.assert_called()
    assert len(contacts) == 1
    assert contacts[0].first_name == "Alice"
    assert contacts[0].email == "alice@example.com"

@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, test_user):
    contact_data = ContactCreate(first_name="John",
        last_name="Doe", email="john@example.com", phone_number="+1234567890",
        birthday=date(2000, 1, 1))
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    contact = Contact(id=1, **contact_data.model_dump(), user=test_user)
    contact_repository.get_contact_by_id = AsyncMock(return_value=contact)

    result = await contact_repository.create_contact(contact_data, test_user)

    mock_session.add.assert_called()
    mock_session.commit.assert_called()
    mock_session.refresh.assert_called()
    assert result.id == 1
    assert result.email == "john@example.com"

@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, test_user):
    contact = Contact(id=1, first_name="John", last_name="Doe",
        email="john@example.com", user=test_user)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.get_contact_by_id(1, test_user)

    mock_session.execute.assert_called()
    assert result == contact

@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, test_user):
    contact = Contact(id=1, first_name="Old",
        last_name="Name", email="old@example.com", user=test_user)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    contact_repository.get_contact_by_id = AsyncMock(return_value=contact)
    update_data = ContactUpdate(first_name="New")

    updated = await contact_repository.update_contact(1, update_data, test_user)

    assert updated.first_name == "New"
    mock_session.commit.assert_called()
    mock_session.refresh.assert_called()

@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, test_user):
    contact = Contact(id=1, first_name="ToDelete",
        last_name="Now", email="delete@example.com", user=test_user)
    mock_session.commit = AsyncMock()
    mock_session.delete = AsyncMock()
    contact_repository.get_contact_by_id = AsyncMock(return_value=contact)

    deleted = await contact_repository.remove_contact(1, test_user)

    mock_session.delete.assert_called_with(contact)
    mock_session.commit.assert_called()
    assert deleted.id == 1

@pytest.mark.asyncio
async def test_get_upcoming_birthdays(contact_repository, mock_session, test_user):
    contact = Contact(
        id=2,
        first_name="Bob",
        last_name="Birthday",
        email="bob@example.com",
        phone_number="+9876543210",
        birthday=date.today(),
        user=test_user
    )
    result_proxy = MagicMock()
    result_proxy.scalars().all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=result_proxy)

    contacts = await contact_repository.get_upcoming_birthdays(0, 10, test_user)

    mock_session.execute.assert_called()
    assert len(contacts) == 1
    assert contacts[0].email == "bob@example.com"