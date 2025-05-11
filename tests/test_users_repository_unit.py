import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.users import UserRepository
from src.database.models import User
from src.schemas import UserCreate

@pytest.fixture
def mock_session():
    return AsyncMock(іspec=AsyncSession)

@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)

@pytest.fixture
def test_user():
    return User(id=1, username="inna", email="inna@example.com", confirmed=False)

@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session, test_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute.return_value = mock_result

    result = await user_repository.get_user_by_id(1)
    assert result == test_user

@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session, test_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute.return_value = mock_result

    result = await user_repository.get_user_by_username("inna")
    assert result == test_user

@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session, test_user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_user
    mock_session.execute.return_value = mock_result

    result = await user_repository.get_user_by_email("inna@example.com")
    assert result == test_user

@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):
    user_data = UserCreate(username="inna", email="inna@example.com", password="hashedpass")
    mock_session.refresh = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.add = MagicMock()

    created_user = await user_repository.create_user(user_data, avatar="http://avatar.url")

    mock_session.add.assert_called()
    mock_session.commit.assert_called()
    mock_session.refresh.assert_called()
    assert created_user.username == "inna"
    assert created_user.avatar == "http://avatar.url"
    assert created_user.hashed_password == "hashedpass"

@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session, test_user):
    user_repository.get_user_by_email = AsyncMock(return_value=test_user)
    mock_session.commit = AsyncMock()

    await user_repository.confirmed_email("inna@example.com")

    assert test_user.confirmed is True
    mock_session.commit.assert_called()

@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session, test_user):
    user_repository.get_user_by_email = AsyncMock(return_value=test_user)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    updated_user = await user_repository.update_avatar_url("inna@example.com", "http://new.avatar")

    assert updated_user.avatar == "http://new.avatar"
    mock_session.commit.assert_called()
    mock_session.refresh.assert_called()
