"""
Repository layer for user-related database operations.

Provides methods for querying and manipulating user records asynchronously using SQLAlchemy.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate

class UserRepository:
    """
    Handles all user-related database interactions.

    Includes methods for retrieving users by ID, username, or email,
    creating new users, confirming email addresses, and updating avatars.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with an asynchronous database session.

        Args:
            session (AsyncSession): SQLAlchemy async session.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their unique ID.

        Args:
            user_id (int): The user's ID.

        Returns:
            User | None: The user object if found, otherwise None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.

        Args:
            username (str): The user's username.

        Returns:
            User | None: The user object if found, otherwise None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.

        Args:
            email (str): The user's email.

        Returns:
            User | None: The user object if found, otherwise None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new user in the database.

        Args:
            body (UserCreate): The data to create the user.
            avatar (str, optional): The avatar URL for the user.

        Returns:
            User: The newly created user object.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Mark a user's email address as confirmed.

        Args:
            email (str): The user's email address.
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update the avatar URL for a user.

        Args:
            email (str): The user's email address.
            url (str): The new avatar URL.

        Returns:
            User: The updated user object.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
